import request from '@/utils/request'

export function ImgList(data) {
  if(data === undefined){
    data = ""
  }
  return request({
    url: '/images/?query='+data,
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

export function ContainerHisory() {
  return request({
    url: '/container/',
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

