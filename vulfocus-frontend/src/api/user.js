import request from '@/utils/request'

export function login(data) {
  return request({
    url: '/user/login',
    method: 'post',
    data
  })
}

export function userList(page) {
  return request({
    url: '/user/?page='+page,
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

export function login_auth(data) {
  return request({
    url: '/login/',
    method: 'post',
    data
  })
}

export function sendMail(data) {
  return request({
    url: '/send_email/',
    method: 'post',
    data
  })
}

export function valMail(data) {
  return request({
    url: '/reset_password/1/',
    method: 'patch',
    data
  })
}

export function updatePassword(data) {
  return request({
    url: '/changepassword/1/',
    method: 'patch',
    data
  })
}
