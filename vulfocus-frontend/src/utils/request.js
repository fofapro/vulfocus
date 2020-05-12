import axios from 'axios'
import { MessageBox, Message } from 'element-ui'
import store from '@/store'
import { getToken } from '@/utils/auth'

// create an axios instance
const service = axios.create({
  baseURL: process.env.VUE_APP_BASE_API, // url = base url + request url
  // withCredentials: true, // send cookies when cross-domain requests
  timeout: 600000 // request timeout
})

// request interceptor
service.interceptors.request.use(
  config => {
    // do something before request is sent

    if (store.getters.token) {
      // let each request carry token
      // ['X-Token'] is a custom headers key
      // please modify it according to the actual situation
      config.headers['Authorization'] = "BMH "+getToken()
    }
    return config
  },
  error => {
    // do something with request error
    // console.log(error) // for debug
    return Promise.reject(error)
  }
)

// response interceptor
service.interceptors.response.use(
  /**
   * If you want to get http information such as headers or status
   * Please return  response => response
  */

  /**
   * Determine the request status by custom code
   * Here is just an example
   * You can also judge the status by HTTP Status Code
   */
  response => {
    const res = response
    // console.log("response -->"+ response)

    // if the custom code is not 20000, it is judged as an error.
    if (res.status > 300) {
      // Message({
      //   message:  'Error',
      //   type: 'error',
      //   duration: 5 * 1000
      // })
      if (res.status === 500 || res.status === 401 || res.status === 403) {
        // to re-login
        MessageBox.confirm('You have been logged out, you can cancel to stay on this page, or log in again', 'Confirm logout', {
          confirmButtonText: 'Re-Login',
          cancelButtonText: 'Cancel',
          type: 'warning'
        }).then(() => {
          if(res.status === 401){
            store.dispatch('user/resetToken').then(() => {
              location.reload()
            })
          }
          /**
           * else{
            this.$message({
              type: 'success',
              message: res.data.data
            })
          }
           */
        })
      }
      return Promise.reject(new Error( 'Error'))
    } else {
      return res
    }
  },
  error => {
    let response = error.response
    // console.log(response)
    let status = response.status
    // data
    let data = response.data
    let errorMsg = error.toString();
    if(status === 401 || errorMsg.indexOf("status code 401") > 0){
      store.dispatch('user/resetToken').then(() => {
        location.reload()
      })
    }else if(status === 400){
      if(data["non_field_errors"] != null){
        errorMsg = data["non_field_errors"][0]
      }else if(data["username"] != null ){
        errorMsg = data["username"][0]
      }else if(data["email"] != null ){
        errorMsg = data["email"][0]
      }
    }else if(status === 500){
      errorMsg = "服务器内部错误，请联系管理员"
    }else if(status === 202){
      errorMsg = "端口无效"
    }
    // || errorMsg.indexOf("status code 403") > 0 || errorMsg.indexOf("status code 500") > 0
    Message({
      message: errorMsg,
      type: "error",
      duration: 5 * 1000
    })
    return Promise.reject(error)
  }
)

export default service
