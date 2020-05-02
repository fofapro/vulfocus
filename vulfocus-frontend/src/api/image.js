import request from '@/utils/request'

export function ImageAdd(data) {
  return request({
    url: '/images/',
    method: 'post',
    headers: {
      'Content-Type': 'multipart/form-data'
    },
    data
  })
}

export function ImageDelete(id) {
  return request({
    url: '/images/'+id+'/delete/'
  })
}

export function ImageLocal() {
  return request({
    url: '/images/local/local/'
  })
}

export function ImageLocalAdd(data) {
  return request({
    url: '/images/local/local_add/',
    method: 'post',
    data
  })
}
