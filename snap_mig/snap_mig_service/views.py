from django.http.response import HttpResponse, JsonResponse
from django.shortcuts import render
from .models import OpenStack_Snapshot_info, OpenStack_Instance_info, CloudStack_Snapshot_info, CloudStack_Instance_info

import requests
import json
import copy
import time




'''
[OpenStack]
164.125.70.22/dashboard

[CloudStack]
164.125.70.26:8080
'''


openstack_server = "http://164.125.70.22"
cloudstack_api = "http://164.125.70.26:8080/client/api?"






# 스냅샷 출력
def snap_view(request):
    '''
    스냅샷 정보를 response

    [호출 과정]
    바에서 스냅샷 클릭하면 함수 호출

    [동작 과정]
    1. 프론트에서 user_id가 담긴 body와 함께 요청을 받음
    2. 디비에 있는 스냅샷 테이블에서 요청받은 user_id의 값을 가지고 있는 row를 가져옴
    3. Json 형식으로 response
    '''
    if request.method == "GET":
        auth = request.headers
        userid = auth["userid"]
        openstack_token = auth["openstack-token"]
        cloudstack_apiKey= auth["cloudstack-apiKey"]
        cloudstack_secret_key = auth["cloudstack-secret-key"]


    # ===================OpenStack===================

    # user_id에 해당하는 row들 OpenStack_Snapshot_info 디비에서 가져오기
    openstack_snap_rows = OpenStack_Snapshot_info.objects.filter(user_id=userid)

    res_snap_view = {} # 스냅샷 정보 response할 변수
    snap_val_list = [] # 모든 스냅샷 정보를 list에 담기 위한 변수
    snap_view_dict = {} # 각각의 스냅샷 정보를 dict에 담기 위한 변수
    x_total_count = 0 #프론트로 전달할 스냅샷의 갯수



    for openstack_snap_row in openstack_snap_rows:
        x_total_count += 1
        snap_view_dict["snap_id"] = openstack_snap_row.snap_id
        snap_view_dict["snap_name"] = openstack_snap_row.snap_name
        snap_view_dict["os"] = openstack_snap_row.os_name
        snap_view_dict["created"] = openstack_snap_row.created
        snap_view_dict["snapcloud"] = "openstack"

        snap_val_list.append(copy.deepcopy(snap_view_dict))


    # ===================OpenStack===================




    # ===================CloudStack===================
    
    # user_id에 해당하는 row들 CloudStack_Snapshot_info 디비에서 가져오기
    cloudstack_snap_rows = CloudStack_Snapshot_info.objects.filter(user_id=userid)

    for cloudstack_snap_row in cloudstack_snap_rows:
        x_total_count += 1
        snap_view_dict["snap_id"] = cloudstack_snap_row.snap_id
        snap_view_dict["snap_name"] = cloudstack_snap_row.snap_name
        snap_view_dict["os"] = cloudstack_snap_row.os_name
        snap_view_dict["created"] = cloudstack_snap_row.created
        snap_view_dict["snapcloud"] = "cloudstack"
        snap_val_list.append(copy.deepcopy(snap_view_dict))


    res_snap_view["showsnapshots"] = snap_val_list


    return JsonResponse(res_snap_view, headers={'X-Total-Count': x_total_count,'access-control-expose-headers':'X-Total-Count', 'access-control-allow-origin':'*'})
    # ===================CloudStack===================






    

# 인스턴스 출력
def ins_view(request):
    '''
    인스턴스 정보를 response

    [호출 과정]
    바에서 인스턴스 클릭하면 함수 호출

    [동작 과정]
    1. 프론트에서 user_id가 담긴 body와 함께 요청을 받음
    2. 디비에 있는 인스턴스 테이블에서 요청받은 user_id의 값을 가지고 있는 row를 가져옴
    3. Json 형식으로 response
    '''
    

    if request.method == "GET":
        auth = request.headers
        userid = auth["userid"]
        openstack_token = auth["openstack-token"]
        cloudstack_apiKey= auth["cloudstack-apiKey"]
        cloudstack_secret_key = auth["cloudstack-secret-key"]

    res_ins_view = {} # 인스턴스 정보 response할 변수    
    ins_val_list = [] # 모든 인스턴스 정보를 list에 담기 위한 변수
    ins_view_dict = {} # 각각의 인스턴스 정보를 dict에 담기 위한 변수
    x_total_count = 0 #프론트로 전달할 인스턴스의 갯수

    # ===================OpenStack===================
    # user_id에 해당하는 row들 디비에서 가져오기
    openstack_ins_rows = OpenStack_Instance_info.objects.filter(user_id=userid)

    for openstack_ins_row in openstack_ins_rows:
        x_total_count += 1
        ins_view_dict["ins_id"] = openstack_ins_row.ins_id
        ins_view_dict["ins_name"] = openstack_ins_row.ins_name
        ins_view_dict["vol_id"] = openstack_ins_row.vol_id
        ins_view_dict["os"] = openstack_ins_row.os_name
        ins_view_dict["created"] = openstack_ins_row.created
        ins_view_dict["snapcloud"] = "openstack"
        ins_val_list.append(copy.deepcopy(ins_view_dict))

    # ===================OpenStack===================




    # ===================CloudStack===================
    # user_id에 해당하는 row들 디비에서 가져오기
    cloudstack_ins_rows = CloudStack_Instance_info.objects.filter(user_id=userid)

    for ins_row in cloudstack_ins_rows:
        x_total_count += 1
        ins_view_dict["ins_id"] = ins_row.ins_id
        ins_view_dict["ins_name"] = ins_row.ins_name
        ins_view_dict["vol_id"] = ins_row.vol_id
        ins_view_dict["os"] = ins_row.os_name
        ins_view_dict["created"] = ins_row.created
        ins_view_dict["snapcloud"] = "cloudstack"
        ins_val_list.append(copy.deepcopy(ins_view_dict))

    res_ins_view["showinstances"] = ins_val_list
    # ===================CloudStack===================
    return JsonResponse(res_ins_view, headers={'X-Total-Count': x_total_count,'access-control-expose-headers':'X-Total-Count', 'access-control-allow-origin':'*'})













def create_snapshot(request):
    '''
    스냅샷 생성

    [호출 과정]
    인스턴스 리스트 보여주는 화면에서 생성하려는 인스턴스 선택하고 스냅샷 생성 버튼 누르면 
    해당 함수 호출


    [동작 과정]
    1. 프론트에서 user_id와 인스턴스 id가 담긴 body와 함께 요청을 받음
    2. 디비에 있는 인스턴스 테이블에서 인스턴스 id에 해당하는 row를 찾음
    3. 해당 row에서 vol_id의 값을 추출
    4. snapshot_body에 필요한 정보를 추가하여 스냅샷 생성 api 호출
    5. 스냅샷 생성 api의 response 값을 바탕으로 스냅샷 테이블에 생성한 스냅샷 정보 추가
    6. 성공여부 response
    '''

    if request.method == "POST":
        auth = request.headers
        userid = auth["userid"]
        openstack_token = auth["openstack-token"]
        cloudstack_apiKey= auth["cloudstack-apiKey"]
        cloudstack_secret_key = auth["cloudstack-secret-key"]

    #======================openstack==========================
    # 스냅샷 생성에 필요한 body 
    openstack_snapshot_body = {
        "snapshot": {
            "display_name": "",
            "volume_id": "",
            "force": "true"
        }
    }


    json_openstack_snap_body = json.dumps(openstack_snapshot_body)
    dict_openstack_snap_body = json.loads(json_openstack_snap_body)




    if request.method == "POST":
        openstack = json.loads(request.body)["openstack"] #openstack에 관련된 정보
        cloudstack = json.loads(request.body)["cloudstack"] #cloudstack에 관련된 정보
    

    # 생성하려는 스냅샷 갯수만큼 반복
    for i in range(0,len(openstack)):

        # req받은 인스턴스 id에 해당하는 row
        ins_row = OpenStack_Instance_info.objects.get(ins_id=openstack[i]["ins_id"])
        dict_openstack_snap_body["snapshot"]["display_name"] = ins_row.ins_name + "-snap"
        dict_openstack_snap_body["snapshot"]["volume_id"] = ins_row.vol_id


        #스냅샷 생성 api
        create_snapshot_res = requests.post(openstack_server+"/compute/v2.1/os-snapshots",
            headers = {'X-Auth-Token' : openstack_token,
                       'content-type' : 'application/json'},
            data=json.dumps(dict_openstack_snap_body)).json()




        # 스냅샷 생성 시간
        secs = time.time()
        tm = time.gmtime(secs)
        created_time=''
        created_time = str(tm.tm_year)+"-"+str(tm.tm_mon)+"-"+str(tm.tm_mday)+" "+str(tm.tm_hour + 9)+":"+str(tm.tm_min)+":"+str(tm.tm_sec)
    

        # 생성한 스냅샷 db에 추가
        OpenStack_Snapshot_Info = OpenStack_Snapshot_info(snap_id = create_snapshot_res["snapshot"]["id"],
                                user_id = userid,
                                snap_name = create_snapshot_res["snapshot"]["displayName"],
                                os_name = ins_row.os_name,
                                created = created_time
                                )

        OpenStack_Snapshot_Info.save()



    

    #======================openstack==========================



    #======================cloudstack==========================
    '''
    cloudstack에서는 snapshot 만들 때, 해당 인스턴스의 상태가 stopped가 되어야 한다.
    필수적으로 필요한 파라미터는 vol_id이고, 추가적으로 스냅샷 name을 지정하기 위해 name 파라미터도 추가한다.

    1. 생성하려는 인스턴스의 id를 프론트로 전달받는다.
    2. 해당 id의 인스턴스를 stopVirtualMachine api를 사용하여 가상머신을 중지한다.(이때 바로 중지하기 위해 'forced' 파라미터 사용)
    3. 생성하려는 인스턴스의 id를 받아서 이에 해당하는 vol_id를 디비에서 받아온다.
    4. 이를 이용해 snapshot 생성
    5. 스냅샷 생성하고 인스턴스는 다시 start해준다.
    6. 생성된 snapshot 정보 db에 저장
    '''


    
    # Signature 생성에 필요한 body (createSnapshot)
    stopVirtualMachine_Signature_body = {
        "requests" : {
            "apiKey": cloudstack_apiKey,
            "response" : "json",
            "command" : "stopVirtualMachine",
            "id" : "",
            "forced" : "true"
        },
        "secretKey" : cloudstack_secret_key
    }

    json_stopVirtualMachine_Signature_body = json.dumps(stopVirtualMachine_Signature_body)
    dict__stopVirtualMachine_Signature_body = json.loads(json_stopVirtualMachine_Signature_body)


    # Signature 생성에 필요한 body (createSnapshot)
    createSnapshot_Signature_body = {
        "requests" : {
            "apiKey": cloudstack_apiKey,
            "response" : "json",
            "command" : "createSnapshot",
            "volumeid" : "",
            "name" : ""
        },
        "secretKey" : cloudstack_secret_key
    }


    json_createSnapshot_Signature_body = json.dumps(createSnapshot_Signature_body)
    dict__createSnapshot_Signature_body = json.loads(json_createSnapshot_Signature_body)




    # Signature 생성에 필요한 body (startVirtualMachine)
    startVirtualMachine_Signature_body = {
        "requests" : {
            "apiKey": cloudstack_apiKey,
            "response" : "json",
            "command" : "startVirtualMachine",
            "id" : ""
        },
        "secretKey" : cloudstack_secret_key
    }

    json_startVirtualMachine_Signature_body = json.dumps(startVirtualMachine_Signature_body)
    dict__startVirtualMachine_Signature_body = json.loads(json_startVirtualMachine_Signature_body)








    for i in range(0,len(cloudstack)):

        ins_row = CloudStack_Instance_info.objects.get(ins_id=cloudstack[i]["ins_id"])

        dict__stopVirtualMachine_Signature_body["requests"]["id"] = ins_row.ins_id

        # stopVirtualMachine Signature URL 생성
        stopVirtualMachine_signature_url = requests.post("https://tyfgmh9pg3.execute-api.ap-northeast-2.amazonaws.com/PROD/signature",
            data=json.dumps(dict__stopVirtualMachine_Signature_body)).json()

        # stopVirtualMachine api
        stopVirtualMachine_res =  requests.get(cloudstack_api + stopVirtualMachine_signature_url).json()

        time.sleep(5)




        dict__createSnapshot_Signature_body["requests"]["volumeid"] = ins_row.vol_id
        dict__createSnapshot_Signature_body["requests"]["name"] = ins_row.ins_name + "-snap"


        # createSnapshot Signature URL 생성
        createSnapshot_signature_url = requests.post("https://tyfgmh9pg3.execute-api.ap-northeast-2.amazonaws.com/PROD/signature",
            data=json.dumps(dict__createSnapshot_Signature_body)).json()




        # createSnapshot api
        createSnapshot_res =  requests.get(cloudstack_api + createSnapshot_signature_url).json()


        # 중지시킨 인스턴스 재시작
        dict__startVirtualMachine_Signature_body["requests"]["id"] = ins_row.ins_id

        # startVirtualMachine Signature URL 생성
        startVirtualMachine_signature_url = requests.post("https://tyfgmh9pg3.execute-api.ap-northeast-2.amazonaws.com/PROD/signature",
            data=json.dumps(dict__startVirtualMachine_Signature_body)).json()

        # startVirtualMachine api
        startVirtualMachine_res =  requests.get(cloudstack_api + startVirtualMachine_signature_url).json()




        # 스냅샷 생성 시간
        secs = time.time()
        tm = time.gmtime(secs)
        created_time=''
        created_time = str(tm.tm_year)+"-"+str(tm.tm_mon)+"-"+str(tm.tm_mday)+" "+str(tm.tm_hour + 9)+":"+str(tm.tm_min)+":"+str(tm.tm_sec)
    


        # # 생성한 스냅샷 db에 추가
        CloudStack_Snapshot_Info = CloudStack_Snapshot_info(snap_id = createSnapshot_res["createsnapshotresponse"]["id"],
                                user_id = userid,
                                snap_name = dict__createSnapshot_Signature_body["requests"]["name"],
                                os_name = ins_row.os_name,
                                created = created_time)

        CloudStack_Snapshot_Info.save()








    a={}
    return JsonResponse(a, safe=False)

   







def delete_snapshot(request):
    """ 
    스냅샷 삭제

    [호출 과정]
    스냅샷 리스트 보여주는 화면에서 삭제하려는 스냅샷 선택하고 삭제 버튼 누르면 
    해당 함수 호출


    [동작 과정]
    1. 사용자가 삭제할 스냅샷을 선택
    2. 삭제 버튼 클릭
    3. 선택한 스냅샷 정보(스냅샷 이름)를 받아와서 api로 삭제
    4. db에도 삭제한 스냅샷 삭제
    """
    
    if request.method == "DELETE":
        auth = request.headers
        userid = auth["userid"]
        openstack_token = auth["openstack-token"]
        cloudstack_apiKey= auth["cloudstack-apiKey"]
        cloudstack_secret_key = auth["cloudstack-secret-key"]

    #======================openstack==========================


    if request.method == "DELETE":
        openstack = json.loads(request.body)["openstack"] #openstack에 관련된 정보
        cloudstack = json.loads(request.body)["cloudstack"] #cloudstack에 관련된 정보


    # 삭제하려는 스냅샷 갯수만큼 반복
    for i in range(0,len(openstack)):
        openstack_delete_snap_id = openstack[i]["snap_id"]


        # 스냅샷 삭제 api
        openstack_delete_url = openstack_server +"/compute/v2.1/os-snapshots/" + openstack_delete_snap_id
        openstack_delete_snapshot_res = requests.delete(openstack_delete_url,
            headers = {'X-Auth-Token' : openstack_token,
                       'content-type' : 'application/json'})


        # db에서 삭제하려는 스냅샷 id가 포함된 row 삭제
        OpenStack_Snapshot_Info = OpenStack_Snapshot_info.objects.filter(snap_id=openstack_delete_snap_id)
        OpenStack_Snapshot_Info.delete()

    #======================openstack==========================



    #======================cloudstack==========================


    # Signature 생성에 필요한 body (deleteSnapshot)
    deleteSnapshot_Signature_body = {
        "requests" : {
            "apiKey": cloudstack_apiKey,
            "response" : "json",
            "command" : "deleteSnapshot",
            "id" : ""
        },
        "secretKey" : cloudstack_secret_key
    }

    json_deleteSnapshot_Signature_body = json.dumps(deleteSnapshot_Signature_body)
    dict__deleteSnapshot_Signature_body = json.loads(json_deleteSnapshot_Signature_body)




    for i in range(0,len(cloudstack)):
        dict__deleteSnapshot_Signature_body["requests"]["id"] = cloudstack[i]["snap_id"]


        # deleteSnapshot Signature URL 생성
        deleteSnapshot_signature_url = requests.post("https://tyfgmh9pg3.execute-api.ap-northeast-2.amazonaws.com/PROD/signature",
            data=json.dumps(dict__deleteSnapshot_Signature_body)).json()


        # deleteSnapshot api
        deleteSnapshot_res =  requests.get(cloudstack_api + deleteSnapshot_signature_url).json()


        # db에서 삭제하려는 스냅샷 id가 포함된 row 삭제
        CloudStack_Snapshot_Info = CloudStack_Snapshot_info.objects.filter(snap_id=cloudstack[i]["snap_id"])
        CloudStack_Snapshot_Info.delete()








    a=[]
    b=[]
    a.append(b)

    return HttpResponse(a, headers={'Access-Control-Request-Method':'DELETE','access-control-allow-origin':'*'})















def create_server(request):

    """ 
    인스턴스 생성

    [호출 과정]
    스냅샷 리스트 보여주는 화면에서 인스턴스로 생성하려는 스냅샷 선택하고 인스턴스 생성 버튼 누르면
    해당 api 호출


    [동작 과정]
    1. 사용자가 인스턴스 생성하려는 스냅샷 선택
    2. 인스턴스 생성 버튼 클릭
    3. 선택한 스냅샷 정보(스냅샷 이름)를 받아와서 api로 인스턴스 생성
    4. db에 생성한 인스턴스 정보 추가
    """


    if request.method == "POST":
        auth = request.headers
        userid = auth["userid"]
        openstack_token = auth["openstack-token"]
        cloudstack_apiKey= auth["cloudstack-apiKey"]
        cloudstack_secret_key = auth["cloudstack-secret-key"]


    #======================openstack==========================




    server_body = {
        "server" : {
            "name" : "",
            "flavorRef" : "2",
            "networks" : [{
                "uuid" : ""
            }],
            "block_device_mapping_v2": [{
                "uuid": "",
                "source_type": "snapshot",
                "destination_type": "volume",
                "boot_index": 0,
                "volume_size": "1"
            }]
        }
    }

    json_server_body = json.dumps(server_body)
    dict_server_body = json.loads(json_server_body)


    # 네트워크 정보 받아오기
    network_list = requests.get(openstack_server+"/compute/v2.1/os-networks",
    headers = {'X-Auth-Token' : openstack_token,
                'content-type' : 'application/json'}).json()

    for i in range(0,len(network_list["networks"])):
        if network_list["networks"][i]["label"] == "shared":
            network_id = network_list["networks"][i]["id"]

    dict_server_body["server"]["networks"][0]["uuid"] = network_id




    if request.method == "POST":
        openstack = json.loads(request.body)["openstack"] #openstack에 관련된 정보
        cloudstack = json.loads(request.body)["cloudstack"] #cloudstack에 관련된 정보





    #생성하려는 인스턴스 갯수만큼 반복
    for i in range(0,len(openstack)):
	

	
	

        #server_body에 name 추가
        dict_server_body["server"]["name"] = openstack[i]["snap_name"] + "-ins"
        #server_body에 스냅샷 이미지 id 추가
        dict_server_body["server"]["block_device_mapping_v2"][0]["uuid"] = openstack[i]["snap_id"]

        # 인스턴스 생성 api
        server_res = requests.post(openstack_server+"/compute/v2.1/servers",
                        headers = {'X-Auth-Token' : openstack_token,
                                'content-type' : 'application/json'},
                        data = json.dumps(dict_server_body))

        time.sleep(12)

        # 인스턴스 생성 시간
        secs = time.time()
        tm = time.gmtime(secs)
        created_time=''
        created_time = str(tm.tm_year)+"-"+str(tm.tm_mon)+"-"+str(tm.tm_mday)+" "+str(tm.tm_hour + 9)+":"+str(tm.tm_min)+":"+str(tm.tm_sec)
    

        # 생성한 인스턴스에 대한 생성 시간 & volume 정보 받아오기 위해
        instance_detailed = requests.get(openstack_server+"/compute/v2.1/servers/detail",
            headers = {'X-Auth-Token' : openstack_token,
                       'content-type' : 'application/json'}).json()

        snapshot_row = OpenStack_Snapshot_info.objects.get(snap_id=openstack[i]["snap_id"])

        for j in range(0,len(instance_detailed["servers"])):
            if instance_detailed["servers"][j]["name"] == dict_server_body["server"]["name"]:
                
                # db instance 테이블에 생성된 인스턴스 추가
                OpenStack_Instance_Info = OpenStack_Instance_info(ins_id = instance_detailed["servers"][j]["id"],
                                                                    user_id = userid,
                                                                    ins_name = dict_server_body["server"]["name"],
                                                                    vol_id = instance_detailed["servers"][j]["os-extended-volumes:volumes_attached"][0]["id"],
                                                                    os_name = snapshot_row.os_name,
                                                                    created = created_time)
                OpenStack_Instance_Info.save()







    #======================openstack===========================




    #======================cloudstack==========================
    

    '''
    vm 생성 과정
    1. template을 생성할 때 필요한 파라미터(ostypeid)를 알기 위해 ListSnapshot api 사용
    2. snapshot을 template으로 변환
    3. vm 생성할 때 필요한 파라미터(zoneid)를 알기 위해 listZones api 사용
    4. 생성된 template으로 vm 생성
    5. 생성된 vm id의 vol_id를 listVolumes api사용하여 받아옴
    6. vm 정보를 db에 저장
    '''




    # Signature 생성에 필요한 body (ListSnapshot)
    ListSnapshot_Signature_body = {
        "requests" : {
            "apiKey": cloudstack_apiKey,
            "response" : "json",
            "command" : "listSnapshots"
        },
        "secretKey" : cloudstack_secret_key
    }



    json_ListSnapshot_Signature_body = json.dumps(ListSnapshot_Signature_body)
    dict_ListSnapshot_Signature_body = json.loads(json_ListSnapshot_Signature_body)



    # ListSnapshot Signature URL 생성
    ListSnapshot_signature_url = requests.post("https://tyfgmh9pg3.execute-api.ap-northeast-2.amazonaws.com/PROD/signature",
        data=json.dumps(dict_ListSnapshot_Signature_body)).json()

    # ListSnapshot api
    ListSnapshot_res =  requests.get(cloudstack_api + ListSnapshot_signature_url).json()


    # id : ostypeid (template 생성할 때 필요한 ostypeid)
    id_ostypeid = ''




    # Signature 생성에 필요한 body (createTemplate)
    createTemplate_Signature_body = {
        "requests" : {
            "apiKey": cloudstack_apiKey,
            "response" : "json",
            "command" : "createTemplate",
            "displaytext" : "",
            "name" : "",
            "ostypeid" : "",
            "snapshotid" : "",
        },
        "secretKey" : cloudstack_secret_key
    }


    json_createTemplate_Signature_body = json.dumps(createTemplate_Signature_body)
    dict__createTemplate_Signature_body = json.loads(json_createTemplate_Signature_body)




    # Signature 생성에 필요한 body (listZones)
    listZones_Signature_body = {
        "requests" : {
            "apiKey": cloudstack_apiKey,
            "response" : "json",
            "command" : "listZones"
        },
        "secretKey" : cloudstack_secret_key
    }

    json_listZones_Signature_body = json.dumps(listZones_Signature_body)
    dict__listZones_Signature_body = json.loads(json_listZones_Signature_body)



    # listZones Signature URL 생성
    listZones_signature_url = requests.post("https://tyfgmh9pg3.execute-api.ap-northeast-2.amazonaws.com/PROD/signature",
        data=json.dumps(dict__listZones_Signature_body)).json()
    
    # listZones api
    listZones_res =  requests.get(cloudstack_api + listZones_signature_url).json()

    # zone_id (vm 생성하는데 필요)
    zone_id = listZones_res["listzonesresponse"]["zone"][0]["id"]





    # Signature 생성에 필요한 body (deployVirtualMachine)
    deployVirtualMachine_Signature_body = {
        "requests" : {
            "apiKey": cloudstack_apiKey,
            "response" : "json",
            "command" : "deployVirtualMachine",
            "serviceofferingid" : "59d174a1-f975-41c5-804a-9913d76c251b",
            "templateid" : "",
            "zoneid" : "",
            "name" : ""
        },
        "secretKey" : cloudstack_secret_key
    }

    json_deployVirtualMachine_Signature_body = json.dumps(deployVirtualMachine_Signature_body)
    dict__deployVirtualMachine_Signature_body = json.loads(json_deployVirtualMachine_Signature_body)





    # Signature 생성에 필요한 body (listVolumes)
    listVolumes_Signature_body = {
        "requests" : {
            "apiKey": cloudstack_apiKey,
            "response" : "json",
            "command" : "listVolumes"
        },
        "secretKey" : cloudstack_secret_key
    }

    json_listVolumes_Signature_body = json.dumps(listVolumes_Signature_body)
    dict__listVolumes_Signature_body = json.loads(json_listVolumes_Signature_body)














    # 생성하려는 인스턴스 갯수만큼 반복
    for i in range(0,len(cloudstack)):

        dict__createTemplate_Signature_body["requests"]["displaytext"] = cloudstack[i]["snap_name"]
        dict__createTemplate_Signature_body["requests"]["name"] = cloudstack[i]["snap_name"]

        snapshot_row = CloudStack_Snapshot_info.objects.get(snap_id=cloudstack[i]["snap_id"])

        if snapshot_row.os_name == "centos 7":
            id_ostypeid = 'f0eeb557-d57b-11eb-9d77-52540057817c'
        elif snapshot_row.os_name == "ubuntu 16.04":
            id_ostypeid = 'f261c129-d57b-11eb-9d77-52540057817c'
        else :
            id_ostypeid = 'beb559ba-d57b-11eb-9d77-52540057817c'


        dict__createTemplate_Signature_body["requests"]["ostypeid"] = id_ostypeid
        dict__createTemplate_Signature_body["requests"]["snapshotid"] = cloudstack[i]["snap_id"]


        # createTemplate Signature URL 생성
        createTemplate_signature_url = requests.post("https://tyfgmh9pg3.execute-api.ap-northeast-2.amazonaws.com/PROD/signature",
            data=json.dumps(dict__createTemplate_Signature_body)).json()


        # createTemplate api
        createTemplate_res =  requests.get(cloudstack_api + createTemplate_signature_url).json()

        time.sleep(3)


        dict__deployVirtualMachine_Signature_body["requests"]["templateid"] = createTemplate_res["createtemplateresponse"]["id"]
        dict__deployVirtualMachine_Signature_body["requests"]["zoneid"] = zone_id
        dict__deployVirtualMachine_Signature_body["requests"]["name"] = cloudstack[i]["snap_name"] +"-ins"


        # deployVirtualMachine Signature URL 생성
        deployVirtualMachine_signature_url = requests.post("https://tyfgmh9pg3.execute-api.ap-northeast-2.amazonaws.com/PROD/signature",
            data=json.dumps(dict__deployVirtualMachine_Signature_body)).json()



        # deployVirtualMachine api
        deployVirtualMachine_res =  requests.get(cloudstack_api + deployVirtualMachine_signature_url).json()

        time.sleep(6)
        


        # listVolumes Signature URL 생성
        listVolumes_signature_url = requests.post("https://tyfgmh9pg3.execute-api.ap-northeast-2.amazonaws.com/PROD/signature",
            data=json.dumps(dict__listVolumes_Signature_body)).json()


        # listVolumes api
        listVolumes_res =  requests.get(cloudstack_api +listVolumes_signature_url).json()


        for j in range(0, listVolumes_res["listvolumesresponse"]["count"]):
            if listVolumes_res["listvolumesresponse"]["volume"][j]["type"] == "ROOT":
                if listVolumes_res["listvolumesresponse"]["volume"][j]["virtualmachineid"] == deployVirtualMachine_res["deployvirtualmachineresponse"]["id"] :
                    new_ins_vol_id = listVolumes_res["listvolumesresponse"]["volume"][j]["id"]
                    break



        # 인스턴스 생성 시간
        secs = time.time()
        tm = time.gmtime(secs)
        created_time=''
        created_time = str(tm.tm_year)+"-"+str(tm.tm_mon)+"-"+str(tm.tm_mday)+" "+str(tm.tm_hour + 9)+":"+str(tm.tm_min)+":"+str(tm.tm_sec)
    


        # 생성한 인스턴스 db에 추가
        CloudStack_Instance_Info = CloudStack_Instance_info(ins_id = deployVirtualMachine_res["deployvirtualmachineresponse"]["id"],
                                user_id=userid,
                                ins_name = dict__deployVirtualMachine_Signature_body["requests"]["name"],
                                vol_id = new_ins_vol_id,
                                os_name = snapshot_row.os_name,
                                created = created_time)

        CloudStack_Instance_Info.save()




        # 생성한 클라우드스택 인스턴스의 템플릿 삭제
        # Signature 생성에 필요한 body (deleteTemplate)
        deleteTemplate_Signature_body = {
            "requests" : {
                "apiKey": cloudstack_apiKey,
                "response" : "json",
                "command" : "deleteTemplate",
                "id" : ""
            },
            "secretKey" : cloudstack_secret_key
        }

        json_deleteTemplate_Signature_body = json.dumps(deleteTemplate_Signature_body)
        dict_deleteTemplate_Signature_body = json.loads(json_deleteTemplate_Signature_body)
        

        # Signature 생성에 필요한 body (listTemplates)
        listTemplates_Signature_body = {
            "requests" : {
                "apiKey": cloudstack_apiKey,
                "response" : "json",
                "command" : "listTemplates",
                "templatefilter" : "all"
            },
            "secretKey" : cloudstack_secret_key
        }

        json_listTemplates_Signature_body = json.dumps(listTemplates_Signature_body)
        dict_listTemplates_Signature_body = json.loads(json_listTemplates_Signature_body)
        
        # listTemplates Signature URL 생성
        listTemplates_signature_url = requests.post("https://tyfgmh9pg3.execute-api.ap-northeast-2.amazonaws.com/PROD/signature",
            data=json.dumps(dict_listTemplates_Signature_body)).json()

        # listTemplates api
        listTemplates_res =  requests.get(cloudstack_api + listTemplates_signature_url).json()

        for k in range(0,listTemplates_res["listtemplatesresponse"]["count"]):
            if listTemplates_res["listtemplatesresponse"]["template"][k]["name"] == cloudstack[i]["snap_name"]:
                dict_deleteTemplate_Signature_body["requests"]["id"] = listTemplates_res["listtemplatesresponse"]["template"][k]["id"]
                break
        

        # deleteTemplate Signature URL 생성
        deleteTemplate_signature_url = requests.post("https://tyfgmh9pg3.execute-api.ap-northeast-2.amazonaws.com/PROD/signature",
            data=json.dumps(dict_deleteTemplate_Signature_body)).json()

        # deleteTemplate api
        deleteTemplate_res =  requests.get(cloudstack_api + deleteTemplate_signature_url).json()





    a = {}
    return JsonResponse(a, safe=False)
















def migration(request):
    
    """

    **마이그레이션은 한번에 각각 하나의 인스턴스만 마이그레이션 되도록**

    인스턴스 생성할 때, 디비에 os 정보도 함께 저장
    - os 정보
    - flavor(openstack : flavor, cloudstack : serviceofferingname)


    그리고 스냅샷 생성할 때도 인스턴스의 os 정보를 디비에 함께 저장해야함
    그래야지 스냅샷으로 인스턴스 생성할 때, os 정보 저장할 수 있음




    [오픈스택 -> 클라우드 스택]
    1. 웹에서 인스턴스 id와 name request body로 넘겨주기
    2. list server deatil api 사용해서 해당 인스턴스 flavor 정보 찾기
    3. 디비에 저장된 해당 os에 해당하는 template과 flavor를 바탕으로 deployvirtualmachine api 사용하여 생성
    4. 디비에 추가
    5. 오픈스택에 인스턴스 삭제
    6. 디비에서 삭제



    [클라우드 스택 -> 오픈스택]
    1. 웹에서 인스턴스 id와 name request body로 넘겨주기
    2. listVirtualMachines api 사용해서 flavor 정보 찾기
    3. 오픈스택 인스턴스 생성할 네트워크 정보 받아오기
    4. 클라우드스택의 인스턴스 os를 바탕으로 인스턴스 이미지 선택
    5. 오픈스택 인스턴스 생성 & 디비에 추가
    6. 클라우드스택 인스턴스 삭제 & 디비에서 삭제


    """

    if request.method == "POST":
        auth = request.headers
        userid = auth["userid"]
        openstack_token = auth["openstack-token"]
        cloudstack_apiKey= auth["cloudstack-apiKey"]
        cloudstack_secret_key = auth["cloudstack-secret-key"]



    if request.method == "POST":
        openstack = json.loads(request.body)["openstack"] #openstack에 관련된 정보
        cloudstack = json.loads(request.body)["cloudstack"] #cloudstack에 관련된 정보



    #============== openstack -> cloudstack 마이그레이션 ============================


    # # 마이그레이션할 인스턴스 id, name
    if len(openstack) != 0:
        mig_openstack_id = openstack[0]["ins_id"]
        mig_openstack_name = openstack[0]["ins_name"]


        # 마이그레이션할 인스턴스의 flavor 정보 받아오기
        instance_detailed = requests.get("http://164.125.70.22/compute/v2.1/servers/detail",
            headers = {'X-Auth-Token' : openstack_token,
                        'content-type' : 'application/json'}).json()



        
        for i in range(0,len(instance_detailed["servers"])):
            if instance_detailed["servers"][i]["id"] == mig_openstack_id :
                openstack_flavor_id = instance_detailed["servers"][i]["flavor"]["id"]
                if openstack_flavor_id == "1" or openstack_flavor_id == "42" or openstack_flavor_id == "84" or openstack_flavor_id == "c1" or openstack_flavor_id == "d1": 
                    mig_openstack_flavor = "59d174a1-f975-41c5-804a-9913d76c251b" # Small Instance
                else : 
                    mig_openstack_flavor = "7702cc34-5421-4e7a-93ca-0b8df1a0afbf" # Medium Instance

        


        # req받은 인스턴스 id에 해당하는 row
        mig_openstack = OpenStack_Instance_info.objects.get(ins_id=mig_openstack_id)
        mig_openstack_os = mig_openstack.os_name




        # Signature 생성에 필요한 body (listZones)
        listZones_Signature_body = {
            "requests" : {
                "apiKey": cloudstack_apiKey,
                "response" : "json",
                "command" : "listZones"
            },
            "secretKey" : cloudstack_secret_key
        }

        json_listZones_Signature_body = json.dumps(listZones_Signature_body)
        dict__listZones_Signature_body = json.loads(json_listZones_Signature_body)



        # listZones Signature URL 생성
        listZones_signature_url = requests.post("https://tyfgmh9pg3.execute-api.ap-northeast-2.amazonaws.com/PROD/signature",
            data=json.dumps(dict__listZones_Signature_body)).json()

        # listZones api
        listZones_res =  requests.get(cloudstack_api + listZones_signature_url).json()

        # zone_id (vm 생성하는데 필요)
        zone_id = listZones_res["listzonesresponse"]["zone"][0]["id"]





         # Signature 생성에 필요한 body (deployVirtualMachine)
        deployVirtualMachine_Signature_body = {
            "requests" : {
                "apiKey": cloudstack_apiKey,
                "response" : "json",
                "command" : "deployVirtualMachine",
                "serviceofferingid" : "",
                "templateid" : "",
                "zoneid" : "",
                "name" : ""
            },
            "secretKey" : cloudstack_secret_key
        }

        json_deployVirtualMachine_Signature_body = json.dumps(deployVirtualMachine_Signature_body)
        dict_deployVirtualMachine_Signature_body = json.loads(json_deployVirtualMachine_Signature_body)


       # Signature 생성에 필요한 body (listTemplates)
        listTemplates_Signature_body = {
            "requests" : {
                "apiKey": cloudstack_apiKey,
                "response" : "json",
                "command" : "listTemplates",
                "templatefilter" : "all"
            },
            "secretKey" : cloudstack_secret_key
        }


        json_listTemplates_Signature_body = json.dumps(listTemplates_Signature_body)
        dict_listTemplates_Signature_body = json.loads(json_listTemplates_Signature_body)


        # Signature 생성에 필요한 body (listVolumes)
        listVolumes_Signature_body = {
            "requests" : {
                "apiKey": cloudstack_apiKey,
                "response" : "json",
                "command" : "listVolumes"
            },
            "secretKey" : cloudstack_secret_key
        }

        json_listVolumes_Signature_body = json.dumps(listVolumes_Signature_body)
        dict_listVolumes_Signature_body = json.loads(json_listVolumes_Signature_body)

        
        # cloudstack template id 받아오기
        # listTemplates Signature URL 생성
        listTemplates_signature_url = requests.post("https://tyfgmh9pg3.execute-api.ap-northeast-2.amazonaws.com/PROD/signature",
            data=json.dumps(dict_listTemplates_Signature_body)).json()


        # listTemplates api
        listTemplates_res =  requests.get(cloudstack_api + listTemplates_signature_url).json()

        for i in range(0, listTemplates_res["listtemplatesresponse"]["count"]):
            # openstack 인스턴스의 os에 해당하는 템플릿 id
            if listTemplates_res["listtemplatesresponse"]["template"][i]["displaytext"] == mig_openstack_os:
                cloudstack_template_id = listTemplates_res["listtemplatesresponse"]["template"][i]["id"]
                break

        dict_deployVirtualMachine_Signature_body["requests"]["serviceofferingid"] = mig_openstack_flavor
        dict_deployVirtualMachine_Signature_body["requests"]["templateid"] = cloudstack_template_id
        dict_deployVirtualMachine_Signature_body["requests"]["zoneid"] = zone_id
        dict_deployVirtualMachine_Signature_body["requests"]["name"] = mig_openstack_name



       # deployVirtualMachine Signature URL 생성
        deployVirtualMachine_signature_url = requests.post("https://tyfgmh9pg3.execute-api.ap-northeast-2.amazonaws.com/PROD/signature",
            data=json.dumps(dict_deployVirtualMachine_Signature_body)).json()


        # deployVirtualMachine api
        deployVirtualMachine_res =  requests.get(cloudstack_api + deployVirtualMachine_signature_url).json()

        time.sleep(4)


        # 인스턴스 생성 시간
        secs = time.time()
        tm = time.gmtime(secs)
        created_time=''
        created_time = str(tm.tm_year)+"-"+str(tm.tm_mon)+"-"+str(tm.tm_mday)+" "+str(tm.tm_hour + 9)+":"+str(tm.tm_min)+":"+str(tm.tm_sec)
          



        # cloudstack에 생성한 인스턴스의 volume id 구하기
        # listVolumes Signature URL 생성
        listVolumes_signature_url = requests.post("https://tyfgmh9pg3.execute-api.ap-northeast-2.amazonaws.com/PROD/signature",
            data=json.dumps(dict_listVolumes_Signature_body)).json()


        # listVolumes api
        listVolumes_res =  requests.get(cloudstack_api + listVolumes_signature_url).json()


        for i in range(0, listVolumes_res["listvolumesresponse"]["count"]):
            if listVolumes_res["listvolumesresponse"]["volume"][i]["type"] == "ROOT":
                if listVolumes_res["listvolumesresponse"]["volume"][i]["virtualmachineid"] == deployVirtualMachine_res["deployvirtualmachineresponse"]["id"] :
                    new_ins_vol_id = listVolumes_res["listvolumesresponse"]["volume"][i]["id"]
                    break


                


        

        # 생성한 클라우드 스택 인스턴스 db에 추가
        CloudStack_Instance_Info = CloudStack_Instance_info(ins_id = deployVirtualMachine_res["deployvirtualmachineresponse"]["id"],
                                user_id = userid,
                                ins_name = mig_openstack_name,
                                vol_id = new_ins_vol_id,
                                os_name = mig_openstack_os,
                                created = created_time)

        CloudStack_Instance_Info.save()








        # 오픈스택 인스턴스 삭제
        delete_instance_url = openstack_server+"/compute/v2.1/servers/" + mig_openstack_id

        openstack_delete_instance_res = requests.delete(delete_instance_url,
            headers = {'X-Auth-Token' : openstack_token,
                    'content-type' : 'application/json'})


        # 삭제할 오픈스택 인스턴스 db에 삭제
        OpenStack_Instance_Info = OpenStack_Instance_info.objects.filter(ins_id=mig_openstack_id)
        OpenStack_Instance_Info.delete()





        #============== openstack -> cloudstack 마이그레이션 ============================





        #============== cloudstack -> openstack 마이그레이션 ============================


    if len(cloudstack) != 0:
        # 마이그레이션할 인스턴스 id, name
        mig_cloudstack_id = cloudstack[0]["ins_id"]
        mig_cloudstack_name = cloudstack[0]["ins_name"]


        server_body = {
            "server" : {
                "name" : "",
                "flavorRef" : "",
                "networks" : [{
                    "uuid" : ""
                }],
                "block_device_mapping_v2": [{
                    "uuid": "",
                    "source_type": "image",
                    "destination_type": "volume",
                    "boot_index": 0,
                    "volume_size": "1"
                }]
            }
        }


        json_server_body = json.dumps(server_body)
        dict_server_body = json.loads(json_server_body)

        # body에 추가
        dict_server_body["server"]["name"] = mig_cloudstack_name


        # 마이그레이션할 인스턴스의 flavor 정보 받아오기
        # Signature 생성에 필요한 body (listVirtualMachines)
        listVirtualMachines_Signature_body = {
            "requests" : {
                "apiKey": cloudstack_apiKey,
                "response" : "json",
                "command" : "listVirtualMachines"
            },
            "secretKey" : cloudstack_secret_key
        }

        json_listVirtualMachines_Signature_body = json.dumps(listVirtualMachines_Signature_body)
        dict_listVirtualMachines_Signature_body = json.loads(json_listVirtualMachines_Signature_body)

        # listVirtualMachines Signature URL 생성
        listVirtualMachines_signature_url = requests.post("https://tyfgmh9pg3.execute-api.ap-northeast-2.amazonaws.com/PROD/signature",
            data=json.dumps(dict_listVirtualMachines_Signature_body)).json()


        # listVirtualMachines api
        listVirtualMachines_res =  requests.get(cloudstack_api + listVirtualMachines_signature_url).json()


        for i in range(0,listVirtualMachines_res["listvirtualmachinesresponse"]["count"]):
            if listVirtualMachines_res["listvirtualmachinesresponse"]["virtualmachine"][i]["id"] == mig_cloudstack_id :
                cloudstack_flavor_name = listVirtualMachines_res["listvirtualmachinesresponse"]["virtualmachine"][i]["serviceofferingname"]
                if cloudstack_flavor_name == "Small Instance":
                    mig_cloudstack_flavor = "42" # 
                else :
                    mig_cloudstack_flavor = "2" # m1.small

        # body에 추가
        dict_server_body["server"]["flavorRef"] = mig_cloudstack_flavor



               #오픈스택 네트워크 정보 받아오기
        network_list = requests.get(openstack_server+"/compute/v2.1/os-networks",
        headers = {'X-Auth-Token' : openstack_token,
                    'content-type' : 'application/json'}).json()

        for i in range(0,len(network_list["networks"])):
            if network_list["networks"][i]["label"] == "shared":
                network_id = network_list["networks"][i]["id"]

        # body에 추가
        dict_server_body["server"]["networks"][0]["uuid"] = network_id




         # cloudstack os에 해당하는 이미지 추가
        # req받은 인스턴스 id에 해당하는 row
        mig_cloudstack = CloudStack_Instance_info.objects.get(ins_id=mig_cloudstack_id)
        mig_cloudstack_os = mig_cloudstack.os_name


        #오픈스택 이미지 id 받아오기
        image_list = requests.get(openstack_server+"/compute/v2.1/images",
            headers = {'X-Auth-Token' : openstack_token,
                        'content-type' : 'application/json'}).json()


        for i in range(0, len(image_list['images'])):
            print(image_list["images"][i]["name"])
            if mig_cloudstack_os in image_list["images"][i]["name"] :
                openstack_image_id = image_list["images"][i]["id"]
                break

        # body에 추가
        dict_server_body["server"]["block_device_mapping_v2"][0]["uuid"] = openstack_image_id


        # 오픈스택 인스턴스 생성 api
        server_res = requests.post(openstack_server+"/compute/v2.1/servers",
                        headers = {'X-Auth-Token' : openstack_token,
                                'content-type' : 'application/json'},
                        data = json.dumps(dict_server_body))


        time.sleep(12)



        # 인스턴스 생성 시간
        secs = time.time()
        tm = time.gmtime(secs)
        created_time=''
        created_time = str(tm.tm_year)+"-"+str(tm.tm_mon)+"-"+str(tm.tm_mday)+" "+str(tm.tm_hour + 9)+":"+str(tm.tm_min)+":"+str(tm.tm_sec)
          



       # 생성한 인스턴스에 대한 생성시간&volume정보 받아오기 위해
        instance_detailed = requests.get(openstack_server+"/compute/v2.1/servers/detail",
            headers = {'X-Auth-Token' : openstack_token,
                        'content-type' : 'application/json'}).json()


        for i in range(0,len(instance_detailed["servers"])):
            if instance_detailed["servers"][i]["name"] == mig_cloudstack_name:

                # db instance 테이블에 생성된 인스턴스 추가
                OpenStack_Instance_Info = OpenStack_Instance_info(ins_id = instance_detailed["servers"][i]["id"],
                                                                    user_id = userid,
                                                                    ins_name = mig_cloudstack_name,
                                                                    vol_id = instance_detailed["servers"][i]["os-extended-volumes:volumes_attached"][0]["id"],
                                                                    os_name = mig_cloudstack_os,
                                                                    created = created_time)
                OpenStack_Instance_Info.save()                







    
        # 클라우드스택 인스턴스 삭제
        # Signature 생성에 필요한 body (destroyVirtualMachine)

        destroyVirtualMachine_Signature_body = {
            "requests" : {
                "apiKey": cloudstack_apiKey,
                "response" : "json",
                "command" : "destroyVirtualMachine",
                "id" : "",
                "expunge" : "true",
                "volumeids" :""

            },
            "secretKey" : cloudstack_secret_key
        }

        json_destroyVirtualMachine_Signature_body = json.dumps(destroyVirtualMachine_Signature_body)
        dict_destroyVirtualMachine_Signature_body = json.loads(json_destroyVirtualMachine_Signature_body)

        dict_destroyVirtualMachine_Signature_body["requests"]["id"] = mig_cloudstack_id


        cloudstack_db = CloudStack_Instance_info.objects.get(ins_id=mig_cloudstack_id)
        dict_destroyVirtualMachine_Signature_body["requests"]["volumeids"] = cloudstack_db.vol_id


        # destroyVirtualMachine Signature URL 생성
        destroyVirtualMachine_signature_url = requests.post("https://tyfgmh9pg3.execute-api.ap-northeast-2.amazonaws.com/PROD/signature",
            data=json.dumps(dict_destroyVirtualMachine_Signature_body)).json()

        # destroyVirtualMachine api
        destroyVirtualMachine_res =  requests.get(cloudstack_api + destroyVirtualMachine_signature_url).json()



        # 삭제한 클라우드스택 인스턴스 db에 삭제
        CloudStack_Instance_Info = CloudStack_Instance_info.objects.filter(ins_id=mig_cloudstack_id)
        CloudStack_Instance_Info.delete()




        # ============== cloudstack -> openstack 마이그레이션 ============================
    a = {}
    return JsonResponse(a, safe=False)






