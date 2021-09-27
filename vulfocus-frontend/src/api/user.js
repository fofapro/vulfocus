import request from '@/utils/request'

export function login(data) {
  return request({
    url: '/login/',
    method: 'post',
    data
  })
}

export function userList(page,query) {
  if(page === undefined || page === null){
    page = 1
  }
  if(query === undefined || query == null){
    query = ""
  }
  return request({
    url: '/user/?page='+page+"&query=" + query,
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

export function accessCode(code) {
  if(code === undefined || code == null){
    code = "";
  }
  return request({
    url: '/accesslink?'+"code="+code,
    method: 'get',
  })
}

export function send_reg_mail(data) {
  return request({
    url: '/send_register_email/',
    method: 'post',
    data
  })
}

export function get_captcha() {
  return request({
    url:'refresh_captcha/',
    method:'get',
  })
}


export function accessUpdateCode(code) {
  if(code === undefined || code == null){
    code = "";
  }
  return request({
    url: '/accessupdatelink?'+"code="+code,
    method: 'get',
  })
}

export function uploaduserimgae(data) {
  return request({
    url: '/uploaduserimg/',
    method: 'post',
    headers: {
      'Content-Type': 'multipart/form-data'
    },
    data
  })
}

export function commitComment(data) {
  return request({
    url: 'comment/',
    method: 'post',
    data
  })
}


export function getComment(sceneId) {
  if(sceneId === undefined || sceneId === null){
    sceneId = ''
  }
  return request({
    url: 'comment/?sceneId='+sceneId,
    method: 'get',
  })
}

/**
 * 删除评论
 */
export function CommentDelete(id) {
  return request({
    url: '/comment/'+id+'/delete/'
  })
}


