import request from '@/utils/request'

export function LogList() {
  return request({
    url: '/syslog/',
    method: 'get'
  })
}
