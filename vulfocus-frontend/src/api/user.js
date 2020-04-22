import request from '@/utils/request'

export function login(data) {
  return request({
    url: '/user/login',
    method: 'post',
    data
  })
}

export function userList() {
  return request({
    url: '/user/',
    method: 'get'
  })
}

export function userChangePwd(data,id) {
  return request({
    url: '/user/'+id+'/',
    method: 'PUT',
    data
  })
}

export function getInfo() {
  return request({
    url: '/user/info',
    method: 'get'
    // params: { token }
  })
}

export function logout() {
  return request({
    url: '/user/logout',
    method: 'get'
  })
}

export function register(data) {
  return request({
    url: '/user/register/',
    method: 'post',
    data
  })
}
