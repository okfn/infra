<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN"
"http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
        <head>
                <title>WSFII - Programme</title>
		<title>Register for WSFII, London 1/2 Oct 2005</title>

                <link href="styles/ckan.css" rel="stylesheet" type="text/css" media="screen,projection">
        </head>
        <body>
                <div id="airlock">
                        <div id="top">
                                <h1>WSFII</h1>
                                <h2><a href="http://www.wsfii.org/">World Summit on Free Information Infrastructures</a></h2>
                        </div>
                        <div id="content">




<h1>Register to attend WSFII</h1>
<h2>WSFII is now 'sold out'. You are welcome to still register below but you will be added to the waiting list.</h2>
<?php

include('http.inc');

$lines = file('registered.txt');

$cur_signups = count($lines);

$name = $_POST['name'];
$mbox = $_POST['mbox'];
$desc = $_POST['desc'];
$url = $_POST['url'];
$volunteer = $_POST['volunteer'];

if ($name and $mbox) {

    $add_line = implode('|',array($name,$mbox,$url,$desc,$volunteer,"\n"));

    array_unshift($lines,$add_line);

    $replace_file = implode("",$lines);
    // locking?
    $fp = fopen('registered.txt',"w+");
    if (flock($fp, LOCK_EX)) { // do an exclusive lock
        fwrite($fp, $replace_file);
        flock($fp, LOCK_UN); // release the lock
    }
    fclose($fp);
    $pwd = random_password();
    $result = http_post('lists.okfn.org',80,'/cgi-bin/mailman/subscribe/wsfii-announce',array('email'=>$mbox,'fullname'=>$name,'pw' => $pw,'pw-conf'=>$pw,'email-button'=>'Subscribe'));
    echo("<p>Thank you for registering.</p>");
    echo('<p>We hope to accomodate out-of-towners on the sofa network in London. If you <a href="http://okfn.org/wsfii/wiki/NeedSofaSpace">need somewhere to stay</a> or have <a href="http://okfn.org/wsfii/wiki/OfferSofaSpace">spare space to offer</a> please visit the appropriate page.</p>');
}

?>

<p>
  Please register here if you wish to attend WSFII. WSFII is open to all but our venue has a maximum capacity. A small entrance fee of &pound;10 is planned to help pay for costs but concessions are available.
</p>

<p>If you <a href="http://okfn.org/wsfii/wiki/NeedSofaSpace">need somewhere to stay</a> or have <a href="http://okfn.org/wsfii/wiki/OfferSofaSpace">spare space to offer</a> to attendees to sleep in during the workshops and conference, please visit the corresponding wiki page and add your details.</p>
<h3>Register to attend WSFII</h3>

<form method="post" action="do.nothing.html">
<table class="register">
<tr><td>Name:
</td><td>
<input type="text" name="name">
</td></tr>

<tr><td>Email address:
<br/><span class="notes">This won't be published, but the venue organisers might need to get in touch.</span> 
</td><td>
<input type="text" name="mbox">
</td></tr>

<tr><td>
Interests:
<br/>
</td><td>
<input type="text" name="desc">
</td></tr>

<tr><td>
Web site:
</td><td>
<input type="text" name="url">
</td></tr>


<tr><td colspan="2">
<p>
Please tick this box if you would like to volunteer some help co-ordinating WSFII, a time commitment as small or large as you like.
<br/>

<input type="checkbox" name="volunteer">
</p>
<!-- <input type="submit" value="sign up"/> -->
<p>
You can no longer sign up to WSFII 2005 as it is now over.
</p>
</td></tr>
</table>
</form>





<h3>People who have already registered</h3>

<?php 

echo("<ol>");

foreach ($lines as $l) {
    $l = rtrim($l,"\n");
    $fields = explode("|",$l);
    echo("<li>".$fields[0]);
    $url = $fields[2];
    $m = preg_match('/^http/',$url);
    if ($m == 0) {
        if ($url != NULL) {
            $url = 'http://'.$url;
        }
    }
    if ($fields[3] != NULL) {
	echo(" - ".$fields[3]);
    }
    if ($url != NULL) { 
	echo(" - <a href=\"".$url."\">".$url."</a></li>");
    }
}

echo("<ol>");

?>
<hr/>
<p><a href="http://wsfii.org/">WSFII</a> | <a href="http://okfn.org/wsfii/programme.html">WSFII Programme</a> | <a href="http://okfn.org/wsfii/wiki/">WSFII Wiki</a></p>
</div>
</div>
</body>
</html>
