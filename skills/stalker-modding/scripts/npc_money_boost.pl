#!/usr/bin/perl
# npc_money_boost.pl - Clear Sky: give every NPC profile 2-5 million + infinite money
# Rewrites <money min max infinitive/> in ANY character_desc_*.xml baseline
# (vanilla-from-db, SRP versions, etc). Byte-wise cp1251-safe, idempotent.
# Usage: perl npc_money_boost.pl <gamedata/configs/gameplay>
use strict; use warnings;

my $DIR = shift @ARGV or die "usage: $0 <gameplay_dir>\n";
$DIR =~ s/[\\\/]+$//;
opendir my $dh, $DIR or die "opendir $DIR: $!";
my @files;
while (my $e = readdir $dh) {
    push @files, "$DIR/$e" if -f "$DIR/$e" && $e =~ /^character_desc_.*\.xml$/;
}
closedir $dh;

my $changed = 0;
for my $file (@files) {
    open my $fh, '<:raw', $file or next;
    local $/;
    my $t = <$fh>;
    close $fh;
    my $n = ($t =~ s/<money min="\d+" max="\d+" infinitive="\d+"\/>/<money min="2000000" max="5000000" infinitive="1"\/>/g);
    next unless $n;
    open my $ofh, '>:raw', $file or die "write $file: $!";
    print $ofh $t;
    close $ofh;
    print "updated: $file ($n tags)\n";
    $changed += $n;
}
print "Done. money tags updated: $changed\n";
