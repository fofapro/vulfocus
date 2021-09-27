import request from '@/utils/request'

/**
 * 创建编排环境信息
 * @param data 编排环境信息
 * @constructor
 */
export function layoutCreate(data) {
  return request({
    url: '/layout/',
    method: 'post',
    headers: {
      'Content-Type': 'multipart/form-data'
    },
    data
  })
}

/**
 * 删除编排环境
 * @param id id
 * @constructor
 */
export function layoutDelete(id) {
  return request({
    url: '/layout/'+id+'/delete/'
  })
}

/**
 * 文件上传
 * @param data
 * @returns
 */
export function uploadImage(data) {
  return request({
    url: '/img/upload/',
    method: 'post',
    headers: {
      'Content-Type': 'multipart/form-data'
    },
    data
  })
}

/**
 * 环境查询
 * @param query 查询关键字
 * @param page 页数
 * @param flag 是否发布
 * @returns
 */
export function layoutList(id){
  return request({
    url: '/layout/?id='+id,
    method: 'get'
  })
}

/**
 * 发布环境
 * @param layoutId
 * @returns
 */
export function layoutRelease(layoutId){
  return request({
    url: '/layout/'+layoutId+'/release/',
    method: 'get'
  })
}


export function build_compose(data) {
  return request({
    url: 'build/compose/',
    method: 'post',
    data: data
  })
}

export function update_build_compose(data) {
  return request({
    url: 'update/compose/',
    method: 'post',
    data: data
  })
}


export function show_build_status() {
  return request({
    url: 'show/compose/',
    method: 'get',
  })
}

export function uploadFile(data) {
  return request({
    url: '/file/upload/',
    method: 'post',
    headers: {
      'Content-Type': 'multipart/form-data'
    },
    data
  })
}

export function deleteFile(data) {
  return request({
    url: '/file/delete/',
    method: 'post',
    headers: {
      'Content-Type': 'multipart/form-data'
    },
    data
  })
}

export function download_layout_image(data) {
  return request({
    url: '/download_layout_image/',
    method: 'post',
    data,
  })
}

export function upload_zip_file(data) {
  return request({
    url: '/upload_zip_file/',
    method: 'post',
    headers: {
      'Content-Type': 'multipart/form-data'
    },
    data
  })
}

export function layoutDownload(layoutId){
  return request({
    url:'/layout/'+layoutId+'/download/',
    method: 'get',
    responseType: 'blob'
  })
}

export function downloadWebsiteLayout(data) {
  return request({
    url: '/download/official/website/layout/',
    method: 'post',
    data,
  })
}


export function getOfficialWebsiteLayout() {
  return request({
    url: 'get/official/website/layout',
    method: 'get',
  })
}

export function updateLayoutDesc(layoutId,data){
  return request({
    url:'/layout/'+layoutId+'/update_desc/',
    method: 'post',
    data
  })
}



