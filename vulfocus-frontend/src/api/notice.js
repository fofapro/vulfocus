import request from '@/utils/request'

export function create_notice(data) {
  return request({
    url: '/notice/',
    method: 'post',
    data,
  })
}


export function get_notice(data,page) {
  if (page ==undefined || page==null){
    page=1;
  }
  if(data == undefined){data=''}
  return request({
    url:'/notice/?query='+data+"&page="+page,
    method: 'get',
  })
}


export function delete_notice(id) {
  return request({
    url:'/notice/'+id+'/',
    method: 'delete',
    data:{"id":id},
  })
}

export function public_notice(id) {
  return request({
    url: '/public_notice/',
    method: 'post',
    data:{"id":id}
  })
}

export function get_public_notice(page) {
  if (page ==undefined || page==null){
    page=1;
  };
  return request({
    url: '/get_notices/?page='+page,
    method: 'get'
  })
}


export function get_notifications_count() {
  return request({
    url:'/get_notifications_count/',
    method:'get',
  })
}


export function notice_detail(notice_id) {
  if(notice_id == undefined)notice_id="";
  return request({
    url: '/notice_detail/?notice_id='+notice_id,
    method: 'get'
  })
}


export function get_content(notice_id) {
  return request({
    url: '/get_content/?notice_id='+ notice_id,
    method: 'get',
  })
}

