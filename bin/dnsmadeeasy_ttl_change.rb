require "rubygems"
require "dnsmadeeasy/api"

#sandbox
#api_key = "748f4840-6799-4981-bd81-9a07a6881874"
#secret_key = "9a1680d3-8c58-43e5-87fc-6fc050bab9b3"

api_key = "<get this from the DME interface>"
secret_key = "<get this from the DME interface>"

api = DnsMadeEasy::Api.new(api_key, secret_key)

#To prevent unwanted flooding of the API system, there is a maximum number of
#requests that can be sent in a given time period. This limit is 150 requests per 5
#minute scrolling window. For example, 100 requests could be made in one minute,
#followed by a 5 minute wait, following by 150 requests. 

api_limit = api.requests_remaining.to_i

count = 0
puts api_limit
domains = api.list_domains
domains.each { |domain|
	
begin

	puts 'current_count: ' + count.to_s + ' - limit: ' + api_limit.to_s
	if count <= api_limit
		records = api.list_records(domain)
		count += 1
		#puts records.inspect
		#'[{"name":"ohhsiii","id":6886222,"type":"A","data":"192.168.23.23","gtdLocation":"DEFAULT","ttl":1800},{"name":"wtfbbq","id":6886223,"type":"A","data":"192.168.34.9","gtdLocation":"DEFAULT","ttl":1800},{"name":"whozdat","id":6886224,"type":"A","data":"192.168.23.9","gtdLocation":"DEFAULT","ttl":1800}]'
		#
		

		records.each { |entry|
		begin
			puts 'Current: ' + entry.inspect
			next if entry[:ttl].to_i == 86400
			#Modify records here
			if count <= api_limit
				puts 'Updating records for: ' + domain + ' - ' + entry[:name]
				resp = api.update_record!(domain, entry[:id], {:ttl => 86400})
				count += 1
				puts 'Updated: ' + resp.inspect
				puts '---------------------------------------------------------'
			else
				puts 'skip - ' +   domain + ' - ' + entry[:name]
				raise 	
			end
		rescue  Exception => e
			puts 'We\'ve hit the api limit, backing off for 5 mins...'
			puts e.message 
			puts e.backtrace.inspect
			$stdout.flush
			sleep 300
			count=0
			retry
		end	
			
		}
	else
		raise
	end
	
	$stdout.flush
rescue Exception => e
	puts 'We\'ve hit the api limit, backing off for 5 mins...'
	puts e.message 
	puts e.backtrace.inspect
	$stdout.flush
	sleep 300
	count=0
	retry
end	
}
