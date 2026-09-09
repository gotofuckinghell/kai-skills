#!/usr/bin/perl
# trade_sell_all.pl - Clear Sky: pass 1 of "traders sell everything"
# 1) replace bare-key (NO TRADE) lines in SELL sections with "= 1.7, 1.7"
# 2) append the full master item list to the ROOT of every buy_supplies chain ("= 3, 1.0")
# Usage: perl trade_sell_all.pl <gamedata/configs>
# cp1251 files are handled byte-wise; new lines are CRLF. Backups: <file>.bak_sellall
use strict; use warnings;
use File::Basename;

my $ROOT = shift @ARGV or die "Usage: $0 <gamedata_configs_dir>\n";
$ROOT =~ s/[\\\/]+$//;
my $MISC = "$ROOT/misc";
my $WDIR = "$ROOT/weapons";
my $crlf = "\x0d\x0a";

# ---------- master item list ----------
my %master;
sub list_files {   # glob() splits on spaces in paths - always use readdir
    my ($dir, $re) = @_;
    my @out;
    opendir my $dh, $dir or return @out;
    while (my $e = readdir $dh) {
        push @out, "$dir/$e" if -f "$dir/$e" && $e =~ $re;
    }
    closedir $dh;
    return @out;
}
sub add_secs {
    my ($re, $excl, @files) = @_;
    for my $file (@files) {
        next unless -f $file;
        open my $fh, '<:raw', $file or next;
        while (<$fh>) {
            if (/^\[\s*([^\]]+?)\s*\]/) {
                my $s = $1;
                next if $excl && $s =~ $excl;
                next unless $s =~ $re;
                $master{$s} = 1;
            }
        }
        close $fh;
    }
}
add_secs(qr/^af_/, undef, "$MISC/artefacts.ltx");
add_secs(qr/^[a-z_]/, qr/_hud$/, "$MISC/items.ltx");
add_secs(qr/^wpn_/, qr/_(minigame|up\d*|hud|no_draw_sound|with_scope)$|^wpn_rpg7_missile$/, list_files($WDIR, qr/^w_.*\.ltx$/));
add_secs(qr/^ammo_/, qr/^ammo_base$/, list_files($WDIR, qr/\.ltx$/));
add_secs(qr/^grenade_/, qr/_hud$/, list_files($WDIR, qr/\.ltx$/));
if (-f "$MISC/outfit.ltx") {
    open my $fh, '<:raw', "$MISC/outfit.ltx" or die $!;
    while (<$fh>) {
        if (/^\[\s*([^\]]+?)\s*\]:\s*outfit_base/) {
            $master{$1} = 1 unless $1 eq 'without_outfit';
        }
    }
    close $fh;
}
$master{$_} = 1 for qw(detector_simple detector_advanced detector_elite);

# --- class filter: only sections with a direct `class =` line may be STOCKED ---
# (stock spawns real objects; class-less sections such as artefacts.ltx
#  af_activation_*/af_*_absorbation/af_base hard-FATAL mid-game:
#  "Can't find variable class in [X]", Xr_ini.cpp:453)
my %with_class;
sub collect_class {
    my (@files) = @_;
    for my $file (@files) {
        next unless -f $file;
        open my $f2, '<:raw', $file or next;
        my $cur;
        while (<$f2>) {
            if (/^\[\s*([^\]]+?)\s*\]/) { $cur = $1; next; }
            if (defined $cur && /^\s*class\s*=/) { $with_class{$cur} = 1; }
        }
        close $f2;
    }
}
collect_class(list_files($WDIR, qr/\.ltx$/), "$MISC/items.ltx", "$MISC/artefacts.ltx", "$MISC/outfit.ltx");
my $before = scalar(keys %master);
%master = map { $_ => 1 } grep { $with_class{$_} } keys %master;
$master{$_} = 1 for qw(detector_simple detector_advanced detector_elite);  # sections live in db, valid
print "Master list: ", scalar(keys %master), " items (filtered from $before by class)\n";

my @targets = ("$MISC/trade_generic.ltx", list_files("$MISC/trade", qr/\.ltx$/));
my ($f_sell, $f_stock) = (0, 0);

for my $file (@targets) {
    next unless -f $file;
    open my $fh, '<:raw', $file or die "open $file: $!";
    local $/; my $text = <$fh>; close $fh;
    my $orig = $text;
    my @lines = split /(\r?\n)/, $text;
    my ($section, %sell_keys, @out);
    my $in_sell = 0;

    # section index + parent map (for supplies root resolution)
    my (@sec_start, %parent_of, %sec_of);
    for my $j (0 .. $#lines) {
        my $l = $lines[$j]; next unless defined $l;
        if ($l =~ /^\[\s*([^\]]+?)\s*\]/) {
            push @sec_start, $j;
            $sec_of{$1} = $j;
        }
    }
    for my $j (@sec_start) {
        if ($lines[$j] =~ /^\[\s*([^\]]+?)\s*\]:\s*([^\]]+?)\s*\]$/) {
            $parent_of{$1} = $2;
        }
    }
    sub find_root {
        my ($name) = @_;
        my %seen;
        while (defined $name && exists $parent_of{$name} && !$seen{$name}++) {
            $name = $parent_of{$name};
        }
        return $name;
    }
    # supply chain names from [trader] buy_supplies
    my @supply_names;
    for my $j (@sec_start) {
        my $k = $j + 1;
        while ($k <= $#lines && defined $lines[$k] && $lines[$k] !~ /^\[/) {
            if ($lines[$k] =~ /^\s*buy_supplies\s*=\s*(.*?)\s*$/) {
                my $val = $1;
                while ($val =~ /\{([^{}]*)\}\s*([A-Za-z0-9_\.\-]+)|([A-Za-z0-9_\.\-]+)/g) {
                    push @supply_names, defined $2 ? $2 : $3;
                }
            }
            $k++;
        }
    }
    my %supply_roots;
    $supply_roots{find_root($_)} = 1 for @supply_names;

    # pass 1: clear bare-key bans in sell sections (keep separators!)
    for my $j (0 .. $#lines) {
        my $l = $lines[$j]; next unless defined $l;
        if ($l =~ /^\[\s*([^\]]+?)\s*\]/) {
            $section = $1;
            $in_sell = ($section =~ /sell/i) ? 1 : 0;
            %sell_keys = ();
            push @out, $l;
            next;
        }
        my $body = $l; $body =~ s/\r?\n$//;
        if ($in_sell && $body =~ /^\s*([A-Za-z0-9_\.\-]+)\s*(.*)$/) {
            my ($key, $rest) = ($1, $2);
            next unless $master{$key};
            next if $rest =~ /^\s*=/;   # already has a value
            if ($sell_keys{$key}) {      # an enable line already exists in this section
                $f_sell++;
                next;                    # drop the duplicate ban line
            }
            $sell_keys{$key} = 1;
            push @out, "$key = 1.7, 1.7\t; sell-all mod (was NO TRADE)$crlf";
            $f_sell++;
            next;
        }
        push @out, $l;
    }
    @lines = @out;   # apply pass 1 before pass 2 indexes the file

    # pass 2: append missing master items to each supplies chain ROOT
    if (%supply_roots) {
        my @insert_at;
        for my $root (keys %supply_roots) {
            next unless exists $sec_of{$root};
            my $start = $sec_of{$root};
            my %have;
            my $k = $start + 1;
            while ($k <= $#lines && defined $lines[$k] && $lines[$k] !~ /^\[/) {
                if ($lines[$k] =~ /^\s*([A-Za-z0-9_\.\-]+)\s*[=;]/) { $have{$1} = 1; }
                $k++;
            }
            # keys already supplied by inheritors of this root
            for my $j (@sec_start) {
                my ($nm) = ($lines[$j] =~ /^\[\s*([^\]]+?)\s*\]/);
                next unless $nm && $nm ne $root;
                my $r = $nm; my %seen2;
                while (defined $r && exists $parent_of{$r} && !$seen2{$r}++) { $r = $parent_of{$r}; }
                next unless defined $r && $r eq $root;
                my $k2 = $j + 1;
                while ($k2 <= $#lines && defined $lines[$k2] && $lines[$k2] !~ /^\[/) {
                    if ($lines[$k2] =~ /^\s*([A-Za-z0-9_\.\-]+)\s*[=;]/) { $have{$1} = 1; }
                    $k2++;
                }
            }
            my @missing = sort grep { !$have{$_} } keys %master;
            push @insert_at, [$start, \@missing] if @missing;
        }
        for my $ins (sort { $b->[0] <=> $a->[0] } @insert_at) {  # insert from the end
            my ($start, $items) = @$ins;
            my $block = "";
            $block .= "$_ = 3, 1.0\t; sell-all stock$crlf" for @$items;
            my $end = $start + 1;
            $end++ while $end <= $#lines && defined $lines[$end] && $lines[$end] !~ /^\[/;
            my @new = (@lines[0..$end-1], $block, @lines[$end..$#lines]);
            @lines = @new;
            $f_stock += scalar @$items;
        }
    }

    my $newtext = join '', @lines;
    if ($newtext ne $orig) {
        open my $bfh, '>:raw', "$file.bak_sellall" or die "backup: $!";
        print $bfh $orig; close $bfh;
        open my $ofh, '>:raw', $file or die "write: $!";
        print $ofh $newtext; close $ofh;
        print "MODIFIED: ", basename($file), "\n";
    }
}
print "Done. NO TRADE removed: $f_sell lines, stock items added: $f_stock\n";
