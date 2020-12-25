import request from '@/utils/request'

/**
 * 获取信息
 * @param layoutId
 * @returns
 */
export function sceneGet(layoutId){
  return request({
    url: '/layout/'+layoutId+'/get/',
    method: 'get'
  })
}

/**
 * 启动模式
 * @param layoutId 环境ID
 * @returns
 */
export function sceneStart(layoutId){
  return request({
    url: '/layout/'+layoutId+'/start/',
    method: 'get'
  })
}

/**
 * 关闭模式
 * @param layoutId
 * @returns {AxiosPromise}
 */
export function sceneStop(layoutId){
  return request({
    url: '/layout/'+layoutId+'/stop/',
    method: 'get'
  })
}

/**
 * 提交Flag
 * @param layoutId layoutId
 * @param flag flag
 * @returns
 */
export function sceneFlag(layoutId, flag){
  return request({
    url: '/layout/'+layoutId+'/flag/?flag='+flag,
    method: 'get'
  })
}

/**
 * 排名
 * @param layoutId
 * @returns
 */
export function sceneRank(layoutId,page){
  if (page === undefined || page === null || page < 1){
    page = 1
  }
  return request({
    url: '/layout/'+layoutId+'/rank/?page='+page,
    method: 'get'
  })
}
