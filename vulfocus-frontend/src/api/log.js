import request from '@/utils/request'

export function LogList(data, page) {
  if (data === undefined){
    data = ""
  }
  if (page === undefined){
    page = 1
  }
  return request({
    url: '/syslog/?query='+data+"&page="+page,
    method: 'get'
  })
}
