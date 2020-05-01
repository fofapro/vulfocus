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
