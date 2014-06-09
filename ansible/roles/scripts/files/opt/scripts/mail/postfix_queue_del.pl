#!/usr/bin/perl
 
$REGEXP = shift || die "no email-adress given (regexp-style, e.g. bl.*\@yahoo.com)!";
 
@data = qx</usr/sbin/postqueue -p>;
for (@data) {
  if (/^(\w+)(\*|\!)?\s/) {
     $queue_id = $1;
  }
  if($queue_id) {
    if (/$REGEXP/i) {
      $Q{$queue_id} = 1;
      $queue_id = "";
    }
  }
}
 
#open(POSTSUPER,"|cat") || die "couldn't open postsuper" ;
open(POSTSUPER,"|postsuper -d -") || die "couldn't open postsuper" ;
 
foreach (keys %Q) {
 print "$_ -> $REGEXP\n";
 print POSTSUPER "$_\n";
};
close(POSTSUPER);
