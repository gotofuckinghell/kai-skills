#!/usr/bin/perl
# xray_log_analyzer.pl — быстрый триаж лога X-Ray (S.T.A.L.K.E.R. Clear Sky / CS:COP)
# Использование: perl xray_log_analyzer.pl <файл_лога>
# Лог: Documents/Stalker-STCS/logs/xray_administrator.log (перезаписывается при каждом запуске)
use strict; use warnings;

my $file = shift @ARGV or die "Usage: $0 <logfile>\n";
open my $fh, '<', $file or die "Cannot open $file: $!\n";

my (@errors, @warnings, %lines, $total, @fatal, @stack);
while (my $line = <$fh>) {
    chomp $line;
    $total++;
    $lines{$line}++;
    my $l = lc $line;
    if ($l =~ /stack trace|^stack/) { push @stack, $line }
    if ($l =~ /\bfatal\b|\bcrash\b|\bexception\b|assertion failed|access violation|unhandled/) {
        push @fatal, $line unless $l =~ /heli_crash|crash_\w+_\w+\]/;  # имена секций с 'crash' — ложные
    }
    elsif ($l =~ /^\s*!\s+|\berror\b/) { push @errors, $line }
    elsif ($l =~ /\bwarning\b/) {
        # [NNNN]=[имя_с_warning] — метки секций, ложные
        push @warnings, $line unless $l =~ /^\[\d+\]=/;
    }
}
close $fh;

print "=== $file ===\n";
print "lines: $total | unique: " . scalar(keys %lines) . "\n";

my @sorted = sort { $lines{$b} <=> $lines{$a} } keys %lines;
my $n = 0;
for my $k (@sorted) {
    last if $lines{$k} < 10; last if ++$n > 12;
    my $s = length($k) > 110 ? substr($k,0,110).'...' : $k;
    printf "rep %4d  %s\n", $lines{$k}, $s;
}

print "\nFATAL markers: " . scalar(@fatal) . "\n";
print "  $_\n" for @fatal[0..($#fatal < 12 ? $#fatal : 12)];
print "\nSTACK frames: " . scalar(@stack) . "\n";
print "  $_\n" for @stack[0..($#stack < 15 ? $#stack : 15)];

my %err_uniq; $err_uniq{$_}++ for @errors;
print "\nERROR lines: " . scalar(@errors) . " (unique " . scalar(keys %err_uniq) . ")\n";
for my $e (sort { $err_uniq{$b} <=> $err_uniq{$a} } keys %err_uniq) {
    my $s = length($e) > 130 ? substr($e,0,130).'...' : $e;
    printf "%4d  %s\n", $err_uniq{$e}, $s;
}

my %w_uniq; $w_uniq{$_}++ for @warnings;
print "\nWARNING lines: " . scalar(@warnings) . " (unique " . scalar(keys %w_uniq) . ")\n";
for my $w (sort { $w_uniq{$b} <=> $w_uniq{$a} } keys %w_uniq) {
    my $s = length($w) > 130 ? substr($w,0,130).'...' : $w;
    printf "%4d  %s\n", $w_uniq{$w}, $s;
}
