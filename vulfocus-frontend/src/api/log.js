import request from '@/utils/request'

export function LogList(page) {
  if(page === undefined || page === null){
    page = 1
  }
  return request({
    url: '/syslog/?page='+page,
    method: 'get'
  })
}
