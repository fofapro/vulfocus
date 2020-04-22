import request from '@/utils/request'

export function containerList(flag) {
  return request({
    url: '/container/?flag='+flag,
    method: 'get'
  })
}

export function containerStop(id) {
  return request({
    url: '/container/'+id+'/stop/?flag=list',
    method: 'get'
  })
}

export function containerStart(id) {
  return request({
    url: '/container/'+id+'/start/?flag=list',
    method: 'get'
  })
}

export function containerDel(id) {
  return request({
    url: '/container/'+id+'/delete/?flag=list',
    method: 'delete'
  })
}


