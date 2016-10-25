#!/bin/bash
#


#create schedule 
curl -b cookiefile -H "Content-Type: application/json" -X POST -d '{"name" : "test1", "day" : "1", "value": "100", "kind" : "1"}' -s http://localhost:5000/api/schedule

curl -b cookiefile -H "Content-Type: application/json" -X POST -d '{"name" : "test2", "day" : "10", "value": "200", "kind" : "2"}' -s http://localhost:5000/api/schedule

curl -b cookiefile -H "Content-Type: application/json" -X POST -d '{"name" : "test3", "day" : "20", "value": "400", "kind" : "3"}' -s http://localhost:5000/api/schedule

curl -b cookiefile -H "Content-Type: application/json" -X POST -d '{"user_id" : "1", "schedule_id" : "1", "count" : "10"}' -s http://localhost:5000/api/schedule_user
