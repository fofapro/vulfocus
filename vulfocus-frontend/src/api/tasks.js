import request from '@/utils/request'

/**
 * 根据任务ID获取任务信息
 * @param taskId 任务ID
 */
export function getTask(taskId) {
  return request({
    url: '/tasks/'+taskId+'/get/',
    method: 'get'
  })
}

/**
 * 批量获取任务信息
 * @param data 任务id列表
 */
export function batchTask(data) {
  return request({
    url: '/tasks/batch/batch/',
    method: 'post',
    data
  })
}

/**
 * 获取任务状态进度
 * @param taskId 任务ID
 */
export function progressTask(taskId) {
  return request({
    url: '/tasks/'+taskId+'/progress/',
    method: 'get'
  })
}

export function layoutbathchTask(data) {
  return request({
    url: '/tasks/layout_batch/layout_batch/',
    method: 'post',
    data
  })
}
