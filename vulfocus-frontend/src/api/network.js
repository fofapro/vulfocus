import request from '@/utils/request'

export function NetWorkList(data, page) {
  if (data === undefined){
    data = ""
  }
  if (page === undefined){
    page = 1
  }
  return request({
    url: '/network/?query='+data+"&page="+page,
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
