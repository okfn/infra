<?

// http.inc by nf@bigpond.net.au
// http://nf.wh3rd.net/

function http_post($server, $port, $url, $vars) {

// example:
//  http_post(
//  "www.fat.com",
//  80, 
//  "/weightloss.pl", 
//  array("name" => "obese bob", "age" => "20")
//  );

    $user_agent = "Mozilla/4.0 (compatible; MSIE 5.5; Windows 98)";


    $urlencoded = "";
    while (list($key,$value) = each($vars))
	$urlencoded.= urlencode($key) . "=" . urlencode($value) . "&";
    $urlencoded = substr($urlencoded,0,-1); 

    $content_length = strlen($urlencoded);

    $headers = "POST $url HTTP/1.1
Accept: */*
Accept-Language: en-au
Content-Type: application/x-www-form-urlencoded
User-Agent: $user_agent
Host: $server
Connection: Keep-Alive
Cache-Control: no-cache
Content-Length: $content_length

";
    
    $fp = fsockopen($server, $port, $errno, $errstr);
    if (!$fp) {
	return false;
    }

    fputs($fp, $headers);
    fputs($fp, $urlencoded);
    
    $ret = "";
    while (!feof($fp))
	$ret.= fgets($fp, 1024);
        
    fclose($fp);
    
    return $ret;

}

function random_password() {
$length    = 16;
$key_chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';
$rand_max  = strlen($keychars) - 1;

for ($i = 0; $i < $length; $i++)
{
   $rand_pos  = rand(0, $max);
   $rand_key[] = $key_chars{$rand_pos};
}

$rand_pass = implode('', $rand_key);
return $rand_pass;
}
