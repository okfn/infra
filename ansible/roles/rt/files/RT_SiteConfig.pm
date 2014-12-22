Set( $rtname, "okfn.org" );
Set( $Organization, "okfn.org" );
Set( $WebPath, "" );
Set( $WebPort, 443 );
Set( $WebDomain, "rt.okfn.org" );
Set( $WebSecureCookies, 1 );
Set( $DatabaseHost, $ENV{DB_PORT_5432_TCP_ADDR} );
Set( $DatabasePassword, $ENV{RT_DATABASE_PW} );
Set( $Timezone, "UTC" );
Set( $MaxInlineBody, 0 );

Plugin( "RT::Extension::ActivityReports" );
Plugin( "RT::Extension::ResetPassword" );
Plugin( "RT::Extension::MergeUsers" );
Plugin( "RT::Extension::SpawnLinkedTicketInQueue" );
Plugin('RT::Extension::Nagios');

Plugin( "RT::Extension::CommandByMail" );
Set( @MailPlugins, qw(Auth::MailFrom Filter::TakeAction) );
Set( $CommandByMailHeader, "X-OKF-UZOQU0" );

Plugin( "RT::Extension::RepeatTicket" );
Set( $RepeatTicketCoexistentNumber, 1 ); # Optional
Set( $RepeatTicketLeadTime, 14 ); # Optional
Set( $RepeatTicketSubjectFormat, '__Subject__' );

Set( %FullTextSearch,
    Enable     => 1,
    Indexed    => 1,
    Column     => 'ContentIndex',
    Table      => 'Fulltext',
);

Set( @Active_MakeClicky, qw(httpurl_overwrite short_ticket_link) );

1;
