import request from '@/utils/request'

export function containerList(flag,page,imageId) {
  if(page === undefined || page === null){
    page = 1
  }
  if(imageId === undefined || imageId == null){
    imageId = ""
  }
  return request({
    url: '/container/?flag='+flag+"&page="+page+"&image_id="+imageId,
    method: 'get'
  })
}

export function containerStop(id) {
  return request({
    url: '/container/'+id+'/stop/?flag=list',
    method: 'get'
  })
}

export function containerStart(id) {
  return request({
    url: '/container/'+id+'/start/?flag=list',
    method: 'get'
  })
}

export function containerDel(id) {
  return request({
    url: '/container/'+id+'/delete/?flag=list',
    method: 'delete'
  })
}


