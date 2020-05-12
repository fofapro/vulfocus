import axios from 'axios'


export function search(keyword) {
  let url = "https://hub.docker.com/api/content/v1/products/search?page_size=50&q=vulfocus%2F"+keyword+"&type=image"
  return axios({
    method: 'get',
    url: url,
    headers:{
      "Sec-Fetch-Site": "none",
      "Sec-Fetch-Mode": "cors",
      "Sec-Fetch-Dest": "empty",
      "Accept-Encoding": "gzip, deflate",
      "Accept-Language": "zh-CN,zh;q=0.9",
      "Search-Version": "v3",
    }
  })
}
