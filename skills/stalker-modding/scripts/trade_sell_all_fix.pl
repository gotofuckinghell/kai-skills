#!/usr/bin/perl
# trade_sell_all_fix.pl - Clear Sky: pass 2 of "traders sell everything"
# Clears remaining bare-key (NO TRADE) bans for master items inside BUY sections
# and supplies chains (a child-section ban would override a root stock enable).
# Value conventions: sell = 1.7,1.7 | supplies chain = 3,1.0 | buy = 0.5,0.3
# Usage: perl trade_sell_all_fix.pl <gamedata/configs>/misc
# Backups: <file>.bak_sellall2
use strict; use warnings;
use File::Basename;

my $MISC = shift @ARGV or die "usage: $0 <misc_dir>\n";
$MISC =~ s/[\\\/]+$//;
my $ROOT = $MISC; $ROOT =~ s#/misc$##;
my $WDIR = "$ROOT/weapons";
my $crlf = "\x0d\x0a";

# ---------- master list (same sources as trade_sell_all.pl) ----------
my %master;
sub list_files { my ($dir,$re)=@_; my @o; opendir my $dh,$dir or return @o; while (my $e=readdir $dh) { push @o,"$dir/$e" if -f "$dir/$e" && $e =~ $re; } closedir $dh; return @o; }
sub add_secs { my ($re,$excl,@files)=@_; for my $file (@files) { next unless -f $file; open my $fh,'<:raw',$file or next; while (<$fh>) { if (/^\[\s*([^\]]+?)\s*\]/) { my $s=$1; next if $excl && $s=~$excl; next unless $s=~$re; $master{$s}=1; } } close $fh; } }
add_secs(qr/^af_/, undef, "$MISC/artefacts.ltx");
add_secs(qr/^[a-z_]/, qr/_hud$/, "$MISC/items.ltx");
add_secs(qr/^wpn_/, qr/_(minigame|up\d*|hud|no_draw_sound|with_scope)$|^wpn_rpg7_missile$/, list_files($WDIR, qr/^w_.*\.ltx$/));
add_secs(qr/^ammo_/, qr/^ammo_base$/, list_files($WDIR, qr/\.ltx$/));
add_secs(qr/^grenade_/, qr/_hud$/, list_files($WDIR, qr/\.ltx$/));
open my $fh, '<:raw', "$MISC/outfit.ltx" or die; while (<$fh>) { if (/^\[\s*([^\]]+?)\s*\]:\s*outfit_base/) { $master{$1}=1 unless $1 eq 'without_outfit'; } } close $fh;
$master{$_}=1 for qw(detector_simple detector_advanced detector_elite);

my ($fixed, $mods) = (0, 0);
my @targets = ("$MISC/trade_generic.ltx", list_files("$MISC/trade", qr/\.ltx$/));

for my $file (@targets) {
    next unless -f $file;
    open my $fh, '<:raw', $file or die "open $file: $!";
    local $/; my $text = <$fh>; close $fh;
    my $orig = $text;
    my @lines = split /(\r?\n)/, $text;
    my ($section, @out) = ('', ());

    # parent map + [trader] buy_supplies -> chain names
    my (%parent_of, %sec_start, %supply_chain);
    for my $j (0..$#lines) {
        my $l = $lines[$j]; next unless defined $l;
        if ($l =~ /^\[\s*([^\]]+?)\s*\]\s*(?::\s*([^\]]+?)\s*)?\]$/) {
            my ($nm, $par) = ($1, $2);
            $sec_start{$nm} = $j;
            $parent_of{$nm} = $par if defined $par;
        }
    }
    for my $nm (keys %sec_start) {
        next unless $nm eq 'trader';
        my $k = $sec_start{$nm} + 1;
        while ($k <= $#lines && defined $lines[$k] && $lines[$k] !~ /^\[/) {
            if ($lines[$k] =~ /^\s*buy_supplies\s*=\s*(.*?)\s*$/) {
                my $val = $1;
                while ($val =~ /\{([^{}]*)\}\s*([A-Za-z0-9_\.\-]+)|([A-Za-z0-9_\.\-]+)/g) {
                    my $nm2 = defined $2 ? $2 : $3;
                    my $cur = $nm2; my %seen;
                    while (defined $cur && exists $parent_of{$cur} && !$seen{$cur}++) {
                        $supply_chain{$cur} = 1; $cur = $parent_of{$cur};
                    }
                    $supply_chain{$cur} = 1 if defined $cur;
                }
            }
            $k++;
        }
    }

    my $in_sell = 0;
    for my $j (0..$#lines) {
        my $l = $lines[$j]; next unless defined $l;
        if ($l =~ /^\[\s*([^\]]+?)\s*\]/) {
            $section = $1;
            $in_sell = ($section =~ /sell/i) ? 1 : 0;
            push @out, $l; next;
        }
        my $body = $l; $body =~ s/\r?\n$//;
        if ($body =~ /^\s*;/ || $body !~ /\S/) {
            push @out, $l;   # comments/blank lines: MUST push or lines glue together
            next;
        }
        if ($body =~ /^\s*([A-Za-z0-9_\.\-]+)\s*(.*)$/) {
            my ($key, $rest) = ($1, $2);
            if ($master{$key} && $rest !~ /^\s*=/ && $section ne 'trader') {
                my $val = $in_sell ? "1.7, 1.7" : ($supply_chain{$section} ? "3, 1.0" : "0.5, 0.3");
                my $tag = $in_sell ? "sell-all" : ($supply_chain{$section} ? "stock" : "buy-all");
                push @out, "$key = $val\t; $tag mod (was NO TRADE)$crlf";
                $fixed++;
                next;
            }
        }
        push @out, $l;
    }
    my $newtext = join '', @out;
    if ($newtext ne $orig) {
        open my $bfh, '>:raw', "$file.bak_sellall2" or die "backup: $!";
        print $bfh $orig; close $bfh;
        open my $ofh, '>:raw', $file or die "write: $!";
        print $ofh $newtext; close $ofh;
        print "MODIFIED: ", basename($file), "\n";
        $mods++;
    }
}
print "Done. extra NO TRADE fixed: $fixed in $mods files\n";
