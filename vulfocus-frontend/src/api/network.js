import request from '@/utils/request'

export function NetWorkList(data) {
  if (data === undefined){
    data = ""
  }
  return request({
    url: '/network/?query='+data,
    method: 'get'
  })
}

export function NetWorkAdd(data) {
  return request({
    url: "/network/",
    method: "post",
    data
  })
}

export function NetworkDelete(id) {
  return request({
    url: '/network/'+id+'/',
    method: 'DELETE',
  })
}
