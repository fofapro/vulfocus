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

export function settingimg() {
  return request({
    url: 'get/settingimg',
    method: 'get'
  })
}

export function enterpriseUpdate(data) {
  return request({
    url: '/enterprise/update/',
    method: 'post',
    data
  })
}
