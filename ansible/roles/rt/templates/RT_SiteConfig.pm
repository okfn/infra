Set( $rtname, "okfn.org" );
Set( $Organization, "okfn.org" );
Set( $WebPath, "" );
Set( $WebPort, 443 );
Set( $WebDomain, "rt.okfn.org" );
Set( $WebSecureCookies, 1 );

Set( $DatabaseType, "Pg" );
Set( $DatabaseHost, "{{ rds_server }}" );
Set( $DatabasePort, 5432 );
Set( $DatabaseName, "rt4" );
Set( $DatabaseUser, "rt_user" );
Set( $DatabasePassword, "{{ rt_db_pass }}" );
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
