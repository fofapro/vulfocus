import request from '@/utils/request'

export function settingGet() {
  return request({
    url: '/setting/get',
    method: 'get'
  })
}

export function settingUpdate(data) {
  return request({
    url: '/setting/update/',
    method: 'post',
    data
  })
}
