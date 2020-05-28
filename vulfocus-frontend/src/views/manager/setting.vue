<template>
  <div style="width: 50%">
    <el-form label-width="170px" style="margin-top: 30px" v-loading="loading" :model="data" element-loading-text="修改中">
      <el-form-item label="分享用户名">
        <el-col :span="20">
          <el-input v-model="data.share_username"></el-input>
        </el-col>
        <el-col :span="2" align="center">
          <el-tooltip content="镜像分享时所需要的贡献用户名，建议设置为Github用户名，方便进行统计贡献。" placement="top">
            <i class="el-icon-question"></i>
          </el-tooltip>
        </el-col>
      </el-form-item>
      <el-form-item label="Dockerhub 用户名">
        <el-col :span="20">
          <el-input v-model="data.username"></el-input>
        </el-col>
        <el-col :span="2" align="center">
          <el-tooltip content="镜像分享时所需的登陆用户名，默认情况下无需修改。" placement="top">
            <i class="el-icon-question"></i>
          </el-tooltip>
        </el-col>
      </el-form-item>
      <el-form-item label="Dockerhub Token">
        <el-col :span="20">
          <el-input v-model="data.pwd"></el-input>
        </el-col>
        <el-col :span="2" align="center">
          <el-tooltip content="镜像分享时所需的登陆凭证，默认情况下无需修改。" placement="top">
            <i class="el-icon-question"></i>
          </el-tooltip>
        </el-col>
      </el-form-item>
      <el-form-item label="镜像过期时间（秒）" >
        <el-col :span="20">
          <el-input v-model="data.time"></el-input>
        </el-col>
        <el-col :span="2" align="center">
          <el-tooltip content="镜像获取时间，默认为 30 分钟，最小为 1 分钟，0 为永不过期，修改后下次启动镜像开始生效。" placement="top">
            <i class="el-icon-question"></i>
          </el-tooltip>
        </el-col>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="settingUpdate">修改</el-button>
        <el-button>取消</el-button>
      </el-form-item>
    </el-form>
  </div>
</template>

<script>
  import { settingGet,settingUpdate } from "@/api/setting"
  export default {
    name: 'setting',
    data() {
      return {
        loading: false,
        data: {
          share_username: '',
          username: '',
          pwd: '',
          time: '1800'
        }
      };
    },
    created() {
      this.initSetting()
    },
    methods:{
      initSetting(){
        settingGet().then(response => {
          let rspData = response.data
          if(rspData.status === 200){
            this.data = rspData.data
          }else{
            for(let i; i < rspData.msg.length; i++){
              this.$message({
                message: rspData.msg[i],
                type: "info",
              })
            }
          }
        })
      },
      settingUpdate(){
        let formData = new FormData()
        formData.set("username", this.data.username)
        formData.set("pwd", this.data.pwd)
        formData.set("time", this.data.time)
        formData.set("share_username",this.data.share_username)
        this.loading = true
        settingUpdate(formData).then(response => {
          let rspData = response.data
          this.data = rspData.data
          if(rspData.status === 200){
            for(let i=0; i < rspData.msg.length; i++){
              this.$message({
                message: rspData.msg[i],
                type: "success",
              })
            }
          }else{
            for(let i=0; i < rspData.msg.length; i++){
              this.$message({
                message: rspData.msg[i],
                type: "info",
              })
            }
          }
          this.loading = false
        })
      }
    }
  }
</script>

<style scoped>
</style>
