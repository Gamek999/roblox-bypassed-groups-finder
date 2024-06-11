# Write your code here :-)
import multiprocessing
import time
import requests
import json
from threading import Thread
from multiprocessing import Process, Queue
import aiohttp
import asyncio


#print(time.time()+3600*24*7)


LOG='https://discord.com/api/webhooks/1213914614689964165/ZCzPKsPy6s0EXhyd_vZBbQzjF7bzEw1eq3P96f_sI7Mo2ja336T8goRHr4BCb9EWN/messages/1217442980747546767' #webhook for activity log replace numbes at the end of link with id of some prevous message sent by this webhook (message has to be in the same channel as webhook)

GROUP='https://discord.com/api/webhooks/1217444418638843924/aMU7dCRMH9xiZ9ohFTGHKKfSYHPPDDR1GL5mwngS4pTk-cT1dSGQSzQtQbTenP-KQy' #webhook where found groups will be sent

SPECS='(4 cores EZ_5/3$)'#server specification (optional)

#Ratelimit bypass made by Gamek989 on discord

#Ubuntu Cpu Burner

def chunk_generator(chunks_queue,id_range,requests_per_tick):
    blocked_gids={}
    last_start_id=id_range[0]
    file=open('blocked_ids.txt', "r")
    lines = file.readlines()
    file.close()
    for line in lines:
        if len(line.strip())>0:
            blocked_gids[int(line.strip())]=True
    first_scan=0
    while True:
        ids_list=[]
        for i in range(1980):
            ids=''
            added_ids = 0
            while added_ids < 100:
                if not last_start_id in blocked_gids:
                    ids += str(last_start_id)+','
                    added_ids += 1
                last_start_id += 1
                if last_start_id > id_range[1]:
                    first_scan+=1
                    last_start_id = id_range[0]
                    break
            ids_list.append(ids)
            if first_scan==1:
                break
        chunks_queue.put([True,ids_list])
        if first_scan==1:
            break
    #print(chunks_queue.qsize())
    while True:
        time.sleep(0.1)
        if chunks_queue.qsize()==0:
            print('First Scan Finished')
            time.sleep(50)
            blocked_gids={}
            file=open('blocked_ids.txt', "r")
            lines = file.readlines()
            file.close()
            for line in lines:
                if len(line.strip())>0:
                    blocked_gids[int(line.strip())]=True
            break
    while True:
        if chunks_queue.qsize()<10:
            for i in range(300):
                ids_list=[]
                for i in range(1980):
                    ids=''
                    added_ids = 0
                    while added_ids < 100:
                        if not last_start_id in blocked_gids:
                            ids += str(last_start_id)+','
                            added_ids += 1
                        last_start_id += 1
                        if last_start_id > id_range[1]:
                            last_start_id = id_range[0]
                            blocked_gids={}
                            file=open('blocked_ids.txt', "r")
                            lines = file.readlines()
                            file.close()
                            for line in lines:
                                if len(line.strip())>0:
                                    blocked_gids[int(line.strip())]=True

                    ids_list.append(ids)
                chunks_queue.put([False,ids_list])
        else:
            time.sleep(0.1)



gggg=open('blocked_ids.txt','a')
gggg.close()

def get_detailed_info(owner_queue,log_queue,timeout,file_queue):

    async def check_if_closed(group_id,owner_queue,log_queue,file_queue):
        try:
            async with aiohttp.ClientSession() as session:
                url = 'https://groups.roblox.com/v1/groups/' + str(group_id)
                async with session.get(url,timeout=3) as response:
                    #print('a')
                    response_text = await response.text()
                    data = json.loads(response_text)
                    claimable = True
                    if response.status == 200:
                        if data['owner'] == None :
                            if 'isLocked' in data:
                                if data['isLocked'] == True:
                                    claimable = False
                            if data['publicEntryAllowed'] == False:
                                claimable = False
                            if claimable == False:
                                file_queue.put(['blocked_ids.txt',str(group_id)+'\n'])
                            else:
                                #print('FoundGroup', group_id)
                                hookData= {
                                  "content": SPECS+'https://roblox.com/groups/'+str(group_id),
                                  "username": "Gamek989",
                                  "attachments": [],
                                }

                                requests.post(GROUP,json=hookData)
                        log_queue.put(1)
                    else:
                        owner_queue.put(group_id)
                        print(response_text)
        except Exception as e:

            owner_queue.put(group_id)
            #print(e,'dgd')


    while True:
        while owner_queue.qsize()>200:
            nah=owner_queue.get()
        id_to_check=owner_queue.get()
        #print(owner_queue.qsize(),id_to_check)
        asyncio.run(check_if_closed(id_to_check,owner_queue,log_queue,file_queue))





def worker(log_queue, count_queue, cookies, timeout, owner_queue,chunks_queue,file_queue):
    #print('a')

    async def main(log_queue, count_queue, cookie, timeout, ids, local_count,first_scan,b,file_queue):
        async with aiohttp.ClientSession() as session:
            t = time.time()
            tasks=[]
            for current_id in ids:
                tasks.append(send_req(session,log_queue, count_queue, cookie, timeout, current_id, local_count,first_scan,b,file_queue))
            ids=[]
            await asyncio.gather(*tasks)


    """Worker function to process groups."""
    async def send_req(session,log_queue, count_queue, cookie, timeout, ids, local_count,first_scan,b,file_queue):

        blacklist_not_existin=True

        url = 'https://groups.roblox.com/v2/groups?groupIds='+ids
        cookies = {'.ROBLOSECURITY': cookie}
        ids_check={}
        while True:
            try:
                async with session.get(url, cookies=cookies) as response:
                    response_text = await response.text()
                    data = json.loads(response_text)
                    if 'data' in data:
                        local_count.append(100)#len(data['data']))
                        #print(data['data'])
                        b[0]+=1
                        for i in data['data']:
                            if blacklist_not_existin==True:
                                ids_check[str(i['id'])]=True
                            if i['owner'] is None:
                                if first_scan==False:

                                    #print(str(i['id']))
                                    hookData= {
                                      "content": SPECS+'https://roblox.com/groups/'+str(i['id']),
                                      "username": "Gamek989",
                                      "attachments": [],
                                    }

                                    #requests.post('https://discord.com/api/webhooks/1207783896519802931/w6NItiPIq_cpEn1MVUywChjirqrvskrYOe9WvEaI1ht2Uz0F9M06_mwVyfZLd9kTzMQp',json=hookData)
                                    owner_queue.put(str(i['id']))

                                else:
                                    file_queue.put(['blocked_ids.txt',str(i['id'])+'\n'])
                        if blacklist_not_existin==True:
                            currr=''
                            for i in ids:
                                if i==',':
                                    if not currr in ids_check:
                                        file_queue.put(['blocked_ids.txt',currr+'\n'])
                                    currr=''

                                else:
                                    currr+=i
                    ids_check={}
                    ids=''


                break
            except Exception as e:
                #print(e)
                continue




    local_count = []
    counter = 0
    while True:
        #print(log_queue.qsize(),count_queue.qsize(),owner_queue.qsize(),chunks_queue.qsize(),file_queue.qsize())
        min_end = time.time() + 60
        for cookie in cookies:
            request_data=chunks_queue.get()
            ids_list=request_data[1]
            b=[0]

            try:
                #asyncio.get_event_loop().run_until_complete(main(log_queue, count_queue, cookie, timeout, ids_list, local_count, request_data[0],b,file_queue))
                asyncio.run(main(log_queue, count_queue, cookie, timeout, ids_list, local_count, request_data[0],b,file_queue))
                request_data=[]
                ids_list=[]
            except Exception as e:
                #chunks_queue.put(request_data)
                #print(e,b[0])
                _=0

            for j in range(len(local_count)):
                counter += local_count[0]
                local_count.pop(0)
            count_queue.put(counter)
            counter=0
        if (min_end - time.time())>0:
            time.sleep(min_end - time.time())
        #print('finshed')




if __name__ == '__main__':





    async def check_cookie(session, cookie):
        try:
            async with session.post("https://auth.roblox.com/v2/logout", cookies={'.ROBLOSECURITY': cookie}) as response:
                if 'X-CSRF-TOKEN' in response.headers:
                    return cookie
        except :
            _=0

    async def cookie_checker():
        roblox_cookies ={}
        working_cookies=[]
        with open('cookies.txt', "r") as file:
            for line in file:
                roblox_cookies[line.strip()]=True
        async with aiohttp.ClientSession() as session:
            tasks = [check_cookie(session, cookie) for cookie in roblox_cookies.keys()]
            results = await asyncio.gather(*tasks)
            for i in results:
                if i!=None:
                    working_cookies.append(i)
        return working_cookies
    def file_writer(file_queue):
        while True:
            data=file_queue.get()
            #print(data)
            fa=open(data[0], "a")
            fa.write(data[1])
            fa.close()


    def workers_refresher():
        global workers
        """Function to refresh workers."""
        while True:
            #print(workers)
            curr_workers=workers.copy()
            for i, k in curr_workers.items():
                args = dict(k)
                if not i.is_alive():
                    #print('Worker has crashed: ',i)
                    hookData= {
                      "content": '',
                      "username": "Gamek989",
                      "attachments": [],
                      "embeds": [
                        {
                          "title": "ERROR",
                          "color": 10751,
                          "fields": [
                            {
                              "name": "ERROR",
                              "value": 'Worker Has Crashed. Restarting Process',
                            },
                          ]
                        }
                      ],
                    }
                    #requests.post('https://discord.com/api/webhooks/1207020764000288849/ooaxtiwMobRJ4ZnVffCqVXaWSE8olUI3AH3vx31dTclsBXNVA3bKP9rQEOnyYec_WVTc',json=hookData)
                    worker_ = Process(
                        target=worker,
                        daemon=True,
                        kwargs=args
                    )
                    i.terminate()
                    workers.pop(i)
                    workers[worker_] = args
                    worker_.start()
            time.sleep(2)

    def counter(log_queue, count_queue):
        """Function to count and display total count."""
        total_count = 0
        curr = total_count
        start = time.time()
        rly_start=time.time()
        total_ownerless_count=0
        ownerless_count=0
        while True:
            while log_queue.qsize()>0:
                total_ownerless_count+=1
                log_queue.get()
            if time.time() - start > 120:
               # print(to_check_owner.qsize()
                #print(str(curr * 60/(time.time() - start)/10**6))
                curr = total_count - curr
                ownerless_count=total_ownerless_count-ownerless_count
                hookData= {
                      "content": SPECS,
                      "username": "Gamek989",
                      "attachments": [],
                      "embeds": [
                        {
                          "title": "Activity Log",
                          "color": 3751,
                          "fields": [
                            {
                              "value": "--------------------------------",
                              "name": 'Current Speed Is: ' + str(curr * 60/(time.time() - start)/10**6+0.00001)[:4]+'M/Min Scans',
                            },
                            {
                              "value": "-------------------------------",
                              "name": 'Scanned Since Last Log: ' + str((curr)/10**6)[:str((curr)/10**6).index('.')+2]+'M Groups' ,
                            },
                            {
                              "value": "-------------------------------",
                              "name": 'Scanned Since Script Start: ' + str(int(total_count//10**6))+'M Groups',
                            },
                            {
                              "value": "-------------------------------",
                              "name": 'Scanned Since Last Log: ' + str(ownerless_count)+' Ownerless Groups ' ,
                            },
                            {
                              "value": "-------------------------------",
                              "name": 'Scanned Since Script Start: ' + str(int(total_ownerless_count))+' Ownerless Groups',
                            },
                            {
                              "value": "-------------------------------",
                              "name": 'Last Log Was: ' + str(int((time.time() - start)//1))+' Seconds Ago',
                            },
                            {
                              "value": "-------------------------------",
                              "name": 'Script Uptime: ' + str(int((time.time() - rly_start)//60))+' Minutes',
                            },
                          ]
                        }
                      ],
                    }
                requests.patch(LOG,json=hookData)

                print('Current Speed is: ' + str(curr * 60/(time.time() - start)/10**6+0.00001)[:4] +'M/Min||' ,'-----MADE BY Gamek989 ON DISCORD-----||',  end='\r')

                start = time.time()
                curr = total_count
                ownerless_count=total_ownerless_count
            scanned=count_queue.get()
            total_count += scanned


    manager = multiprocessing.Manager()

    file_queue = Queue()
    count_queue = Queue()
    chunks_queue = Queue()
    to_check_owner=Queue()
    log_queue = Queue()
    blocked_ids = {}

    with open('blocked_ids.txt', "r") as file:
        for line in file:
            blocked_ids[line.strip()]=True







    #id_range = list(map(int, input('Give id range: ').split()))

    try:
        working_cookies = asyncio.run(cookie_checker())
    except:
        exit(0)
    if len(blocked_ids)<2.3*10**(3+2/2+2):
        id_ranges=[[16500000,17500000],[32000000,33800000]]
        ids_per_worker = int((id_ranges[0][1] - id_ranges[0][0]) / len(working_cookies)) + 1

    workers = {}




    kwargs_ = dict(
        owner_queue=to_check_owner,
        log_queue=log_queue,
        timeout=6,  # timeout,
        file_queue=file_queue,
    )

    worker_ = Process(
        target=get_detailed_info,
        daemon=True,
        kwargs=kwargs_
    )
    worker_.start()



    for id_range in id_ranges:
        kwargs_ = dict(
        chunks_queue=chunks_queue,
        id_range=id_range,
        requests_per_tick=600
        )

        worker_ = Process(
            target=chunk_generator,
            daemon=True,
            kwargs=kwargs_
        )
        worker_.start()


    print('Working cookies:',len(working_cookies),' Ids Per Workier: ',ids_per_worker,' Blocked group ids:',len(blocked_ids))
    for i in range(0,len(working_cookies)-2,2):
        ids_per_worker=ids_per_worker
        kwargs_ = dict(
            log_queue=log_queue,
            count_queue=count_queue,
            timeout=6,  # timeout,
            cookies=[working_cookies[i],working_cookies[i+1]],#working_cookies[i+1]],working_cookies[i+2],working_cookies[i+3],working_cookies[i+4],working_cookies[i+5]],
            #gid_range=[id_range[0] + ids_per_worker * i, ids_per_worker * (i + 1) + id_range[0]],
            owner_queue=to_check_owner,
            chunks_queue=chunks_queue,
            file_queue=file_queue,
        )
        if len(blocked_ids)<2.3*10**(3+2/2+2):
            worker_ = Process(
                target=worker,
                daemon=True,
                kwargs=kwargs_
            )
        workers[worker_] = kwargs_
    for worker_ in workers.keys():
        worker_.start()




    t = Thread(target=counter, args=(log_queue, count_queue,))
    t.daemon = True
    t.start()

    t = Thread(target=workers_refresher)
    t.daemon = True
    t.start()

    t = Thread(target=file_writer, args=(file_queue,))
    t.daemon = True
    t.start()

    hookData= {
      "content": SPECS,
      "username": "Gamek989",
      "attachments": [],
      "embeds": [
        {
          "title": "Script Started",
          "color": 109751,
          "fields": [
            {
              "name": "Activity-Log",
              "value": '----------------------------------------\nGroup Finder has succesfully started\n\n\n\n\n\n\n\n\n\n\n----------------------------------------',
            },
            {
              "name": "Working Cookies: "+ str(len(working_cookies)) ,
              "value": '----------------------------------------',
            },
            {
              "name": "Blocked Ids Of "+ str(len(blocked_ids))+' Closed Groups',
              "value": '----------------------------------------',
            },
          ]
        }
      ],
    }
    requests.patch(LOG,json=hookData)



    time.sleep(999999)






