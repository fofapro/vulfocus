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
export function layoutList(query, page, flag){
  if(page === undefined || page === null){
    page = 1
  }
  if(query === undefined || query == null){
    query = ""
  }
  if (flag === undefined || flag === null || flag === ""){
    flag = ""
  }
  return request({
    url: '/layout/?query='+query+"&page="+page+"&flag="+flag,
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
