import request from '@/utils/request'

export function ImgList(data,flag,page) {
  if(data === undefined){
    data = ""
  }
  if(page === undefined || page == null){
    page =1
  }
  let url = "/images/?query="+data+"&page="+page
  let paramFlag = ""
  if(flag === true){
    paramFlag = "flag"
    url += "&flag="+paramFlag
  }
  return request({
    url: url,
    method: 'get'
  })
}

export function ContainerINFO(id) {
  return request({
    url: '/images/'+id,
    method: 'get'
  })
}
export function ContainerSTATUS(id) {
  return request({
    url: '/container/'+id+'/status/',
    method: 'get'
  })
}


export function ContainerSTART(id) {
  return request({
    url: '/images/'+id+'/start/',
    method: 'get'
  })
}

export function ContainerHisory(page) {
  if(page === undefined || page === null || page < 1){
    page = 1
  }
  return request({
    url: '/container/?page='+page,
    method: 'get',
  })
}

export function ContainerDelete(id) {
  return request({
    url: '/container/'+id+'/delete/',
    method: 'delete'
  })
}

export function ContainerStop(id) {
  return request({
    url: '/container/'+id+'/stop/',
    method: 'get'
  })
}

export function SubFlag(id,flag) {
  return request({
    url: '/container/'+id+'/flag/?flag='+flag,
    method: 'get',
  })
}

export function ContainerStart(id) {
  return request({
    url: '/container/'+id+'/start/',
    method: 'get'
  })
}

