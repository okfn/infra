#!/usr/bin/env ruby
#	
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#	Copyright Vincent Reydet

# Project: nagios-check-webpage 
# Website: http://code.google.com/p/nagios-check-webpage/

# To use in nagios:
#   - Put the script into the $USER1$ directory
#   - Add this check command ( add your options ... )
#     define command{
#       command_name  check-webpage
#       command_line  $USER1$/check_webpage.rb -u $ARG1$
#     }

# Quick documentation: use -h option
# Full documentation: http://code.google.com/p/nagios-check-webpage/wiki/Documentation

# TODO
# - check if threadsafe ( totalX+=1 problem )
# - check if inner links search is exhaustive enough ( uppercase element problem ... )

require 'thread'
require 'net/http'
require 'net/https'
require 'open-uri'
require 'rubygems'
require 'hpricot'
require 'optiflag'
require 'zlib'

MAX_REDIRECT=5 #set max redirect to prevent infinite loop

#set http headers
httpHeaders = Hash.new
httpHeaders = { 'User-Agent' => 'nagios-check-webpage' }

## OPT PARSING
###############################################################
module Example extend OptiFlagSet
  usage_flag "h","help"
  optional_switch_flag "v" do
    description "verbose"
  end
  optional_switch_flag "vv" do
    description "more verbose !"
  end
  optional_switch_flag "e" do
    description "extended mode, see the documentation"
  end
  optional_switch_flag "H" do
    long_form "span-hosts"
    description "--span-hosts, download from other hosts"
  end
  optional_flag "c" do
    long_form "critical"
    description "--critical, default 60,  Critical time (s)"
  end
  optional_flag "w" do
    long_form "warn"
    description "--warn, default 5,  warn time (s)"
  end
  optional_flag "w2" do
    long_form "warn2"
    description "--warn2, default 10,  warn2 time (s), use with '-e'"
  end
  optional_flag "k" do
    long_form "key"
    description "--key, check for keyword"
  end
  optional_switch_flag "z" do
    long_form "gzip"
    description "--gzip, add gzip,deflate to http headers"
  end
  optional_switch_flag "n" do
    long_form "no-inner-links"
    description "--no-inner-links, do not dl inner links, get only the html"
  end
  flag "u" do
    long_form "url"
    description "--url, absolute: [http://www.google.com]"
  end

  and_process!
end 

# GET THE ARGV VALUES
if ARGV.flags.e?
  EXTENDED=1
else
  EXTENDED=0
end

if ARGV.flags.vv?
  DEBUG=2
elsif ARGV.flags.v?
  DEBUG=1
else
  DEBUG=0
end

if ARGV.flags.c?
  timeCritical=ARGV.flags.c.to_f
else
  timeCritical=60
end

if ARGV.flags.w?
  timeWarn=ARGV.flags.w.to_f
else
  timeWarn=5
end

if ARGV.flags.w2?
  timeWarn2=ARGV.flags.w2.to_f
else
  timeWarn2=10
end

if ARGV.flags.k?
  keyword=ARGV.flags.k
else
  keyword=nil
end

if ARGV.flags.z?
  gzip=1
  httpHeaders['Accept-Encoding'] = "gzip,deflate"
else
  gzip=0
end

if ARGV.flags.n?
  GET_INNER_LINKS = 0
else
  GET_INNER_LINKS = 1
end

if ARGV.flags.H?
  SPAN_HOSTS=1
else
  SPAN_HOSTS=0
end

inputURL=ARGV.flags.u
REQUEST_TIMEOUT=timeCritical

#reports hashtable init
reports = {}
reports['totalDlTime'] = 0 #Stat total download
reports['totalSize'] = 0 #Stat total size
reports['fileErrorCount'] = 0 #error count
reports['linksToDlCount'] = 0 #links count

if DEBUG >= 2 then puts "\n * ARGS: c=#{timeCritical} w=#{timeWarn} e=#{EXTENDED} w2=#{timeWarn2} u=#{ARGV.flags.u}" end

## PARSE INPUT URL
###############################################################
begin
  if inputURL.index("http") != 0
    inputURL ="http://"+inputURL
  end
  mainUrl = URI.parse(inputURL)
rescue
  puts "Critical: syntax error, can't parse url ..."
  exit 2
end

## COMPLETE THE INPUT URL
###############################################################
if mainUrl.path == "" || mainUrl.path == nil
  mainUrl.path = '/'
end

## Remove ssl certificate warning
#  http://www.5dollarwhitebox.org/drupal/node/64
###############################################################
class Net::HTTP
  alias_method :old_initialize, :initialize
  def initialize(*args)
    old_initialize(*args)
    @ssl_context = OpenSSL::SSL::SSLContext.new
    @ssl_context.verify_mode = OpenSSL::SSL::VERIFY_NONE
  end
end

## get url function
###############################################################
def getUrl( parsedUri, httpHeaders )
  _h = Net::HTTP.new( parsedUri.host, parsedUri.port)
  if parsedUri.scheme == "https"
    _h.use_ssl = true
  end
  if parsedUri.path == "" || parsedUri.path == nil
    parsedUri.path = '/'
  end
  _h.read_timeout=REQUEST_TIMEOUT

  if DEBUG >= 2
  then
    printf " * \nRequest:\n%s\nPath:%s\nHTTP headers:%s\n",_h.to_yaml,parsedUri.to_yaml,httpHeaders.to_yaml
  end

  begin
    if parsedUri.query.nil?
      path = parsedUri.path
    else
      path = parsedUri.path + '?' + parsedUri.query
    end
    r,d = _h.get(path, httpHeaders)
  rescue Timeout::Error
    puts "Critical: timeout #{REQUEST_TIMEOUT}s on [#{parsedUri.path}]"
    exit 2
  rescue
    puts "Critical: error with [#{parsedUri}]: "+$!.to_s
    exit 2
  end

  return r,d
end

## get inner links function
###############################################################
def getInnerLinks (mainUrl, data, httpHeaders, reports)

  ## Parsing main page data
  doc = Hpricot(data)
  parsingResult =                 doc.search("//img[@src]").map { |x| x['src'] }
  parsingResult = parsingResult + doc.search("//script[@src]").map { |x| x['src'] }
  parsingResult = parsingResult + doc.search("//input[@src]").map { |x| x['src'] }
  parsingResult = parsingResult + doc.search("//link[@href]").map { |x| x['href'] }
  parsingResult = parsingResult + doc.search("//embed[@src]").map { |x| x['src'] }

  ## Pop the wanted links
  if DEBUG >= 2 then puts "\n * parsing results (#{parsingResult.length}) ..." end
  linksToDl = []
  parsingResult.length.times do |i|
    #change link to full link
    if parsingResult[i]==nil || parsingResult[i]==""
      if DEBUG >= 2 then puts "#{parsingResult[i]} -> pass (empty)" end
      next
    end
    if parsingResult[i][0,4] != "http" && parsingResult[i][0,1] != "/"
      parsingResult[i]="/"+parsingResult[i];
    end
    if parsingResult[i][0,4] != "http"
      parsingResult[i]= mainUrl.scheme+"://"+mainUrl.host + parsingResult[i]
    end

    begin
      #test if url
      url = URI.parse(URI.escape(parsingResult[i],"[]{}|+"))
      if SPAN_HOSTS == 0 && url.host != mainUrl.host
        if DEBUG >= 2 then puts "#{parsingResult[i]} -> pass" end
        next
      end
    rescue URI::InvalidURIError
      if DEBUG >= 2 then puts "#{parsingResult[i]} -> error" end
      next
    end
    if DEBUG >= 2 then puts "#{parsingResult[i]} -> add" end
    linksToDl.push(url)
  end

  if DEBUG >= 2 then linksToDlPrevCount=linksToDl.length end
  linksToDl.uniq!
  reports['linksToDlCount'] = linksToDl.length
  if DEBUG >= 2 then puts "\n * remove duplicated links: #{linksToDlPrevCount} -> #{linksToDl.length}" end

  ## DL content links with threads
  mutex = Mutex.new #set mutex
  if DEBUG >= 1 then puts "\n * downloading inner links (#{linksToDl.length}) ..." end
  threads = []
  linksToDl.each {  |link|
    threads << Thread.new(link) { |myLink|
      t0 = Time.now
      rhead, rbody = getUrl(myLink, httpHeaders)
      if rbody == nil then
        # Happens when '204 no content' occurs
        rbody = ''
      end
      t1 = Time.now-t0
      mutex.synchronize do
        reports['totalDlTime'] += t1
        reports['totalSize'] += rbody.length
      end
      if rhead.code =~ /[^2]../ then reports['fileErrorCount'] += 1 end
      if DEBUG >= 1 then puts "[#{rhead.code}] #{rhead.message} "+myLink.to_s.gsub(mainUrl.scheme+"://"+mainUrl.host,"")+" -> s(#{rbody.length}o) t("+sprintf("%.2f", t1)+"s)" end
    }
  }
  threads.each { |aThread|  aThread.join }
end

## get main page and parse it
###############################################################
startedTime = Time.now
if DEBUG >= 1 then puts "\n * Get main page: #{mainUrl}" end
rhead,rbody = getUrl(mainUrl, httpHeaders)

# DEBUG headers
if DEBUG >= 2
then 
  printf "\n * response header\n%s",rhead.to_yaml
end

## handle redirectiol
###############################################################
i=0 #redirect count
while rhead.code =~ /3../
  begin
    mainUrl = URI.parse(rhead['location'])
  rescue
    puts "Critical: can't parse redirected url ..."
    exit 2
  end
  if DEBUG >= 1 then puts "   -> #{rhead.code}, main page is now: #{mainUrl}" end
  rhead, rbody = getUrl(mainUrl, httpHeaders)
  if (i+=1) >= MAX_REDIRECT
    puts "Critical: too much redirect (#{MAX_REDIRECT}), exit"
    exit 2
  end
end

## check main url return code
###############################################################
if rhead.code =~ /[^2]../
  puts "Critical: main page rcode is #{rhead.code} - #{rhead.message}"
  exit 2
end

## Get main url page size
###############################################################
reports['totalSize'] = rbody.length

## inflate if gzip is on
###############################################################
if gzip == 1 && rhead['Content-Encoding'] == 'gzip'
  begin
    rbody = Zlib::GzipReader.new(StringIO.new(rbody)).read
  rescue Zlib::GzipFile::Error, Zlib::Error
    puts "Critical: error while inflating gziped url '#{mainUrl}': "+$!.to_s
    exit 2
  end
end

## Check for keyword ( -k option )
###############################################################
if keyword != nil
  hasKey=0
  rbody.each { |line|
    if line =~ /#{keyword}/
      hasKey=1
    end
  }
  if hasKey==0
    puts "Critical: string not found"
    exit 2
  end
end

if DEBUG >= 1 then puts "[#{rhead.code}] #{rhead.message} s(#{reports['totalSize']}) t(#{Time.now-startedTime})" end

## inner links part
###############################################################
getInnerLinks(mainUrl, rbody, httpHeaders, reports) unless GET_INNER_LINKS == 0

## Get Statistics
###############################################################
finishedTime = Time.now
totalTime=finishedTime-startedTime

if DEBUG >= 1
  puts "\n * results"
  puts "Inner links count: #{reports['linksToDlCount']}"
  puts "Inner links dl cumulated time: "+sprintf("%.2f", reports['totalDlTime']) + "s"
  puts "Total time: "+sprintf("%.2f", totalTime)+"s"
  puts "Total size: #{reports['totalSize']/1000}ko"
  puts "\n"
end

## Set exit value
###############################################################
if totalTime < timeWarn # Good \o/
  retCode=0
  retCodeLabel="OK"
elsif EXTENDED == 0 && totalTime >= timeWarn && totalTime < timeCritical # not so good o_o
  retCode=1
  retCodeLabel="Warn"
## - Extended mode begin
elsif EXTENDED == 1 && totalTime >= timeWarn && totalTime < timeWarn2 # not so good o_o
  retCode=1
  retCodeLabel="Warn"
elsif EXTENDED == 1 && totalTime >= timeWarn2 && totalTime < timeCritical # not so good o_o'
  retCode=3
  retCodeLabel="Unknown"
## - Extended mode end
else # bad :(
  retCode=2
  retCodeLabel="Critical"
end

## show the error file count in output
###############################################################
if reports['fileErrorCount'] > 0
  fileErrorStr="/#{reports['fileErrorCount']} err"
else
  fileErrorStr=""
end

## print the script result for nagios
###############################################################
print "#{retCodeLabel} - #{reports['totalSize']/1000}ko, #{reports['linksToDlCount']+1} files#{fileErrorStr}, "+sprintf("%.2f", totalTime)+"s"
print "|time="+sprintf("%.2f", totalTime)+"s;#{timeWarn};#{timeCritical};0.00;#{REQUEST_TIMEOUT} size="+"#{reports['totalSize']/1000}"+"KB;;;0;"
print "\n"
exit retCode
