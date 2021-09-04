<template>
  <div>
    <el-tabs style="margin-left: 20px">
      <el-tab-pane label="系统设置">
        <el-row :gutter="20">
          <el-col :span="12">
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
                  <el-tooltip content="镜像过期时间，默认为 30 分钟，最小为 1 分钟，0 为永不过期，修改后下次启动镜像开始生效。" placement="top">
                    <i class="el-icon-question"></i>
                  </el-tooltip>
                </el-col>
              </el-form-item>
              <el-form-item label="镜像过期删除" >
                <el-col :span="20">
                  <el-switch v-model="data.del_container"></el-switch>
                </el-col>
                <el-col :span="2" align="center">
                  <el-tooltip content="开启之后，镜像到期会自动删除相关容器(默认开启)" placement="top">
                    <i class="el-icon-question"></i>
                  </el-tooltip>
                </el-col>
              </el-form-item>
              <el-form-item label="注册验证" >
                <el-col :span="20">
                  <el-switch v-model="data.cancel_validation"></el-switch>
                </el-col>
                <el-col :span="2" align="center">
                  <el-tooltip content="关闭之后，用户注册将关闭邮箱验证(默认开启)" placement="top">
                    <i class="el-icon-question"></i>
                  </el-tooltip>
                </el-col>
              </el-form-item>
              <el-form-item label="用户注册" >
                <el-col :span="20">
                  <el-switch v-model="data.cancel_registration"></el-switch>
                </el-col>
                <el-col :span="2" align="center">
                  <el-tooltip content="关闭之后，将无法使用注册功能(默认开启)" placement="top">
                    <i class="el-icon-question"></i>
                  </el-tooltip>
                </el-col>
              </el-form-item>
              <el-form-item label="自动下载镜像" >
                <el-col :span="20">
                  <el-switch v-model="data.is_synchronization"></el-switch>
                </el-col>
                <el-col :span="2" align="center">
                  <el-tooltip content="开启之后每隔 1 小时自动下载最新的镜像" placement="top">
                    <i class="el-icon-question"></i>
                  </el-tooltip>
                </el-col>
              </el-form-item>
              <el-form-item>
                <el-button type="primary" @click="settingUpdate">修改</el-button>
                <el-button>取消</el-button>
              </el-form-item>
            </el-form>
          </el-col>
        </el-row>
      </el-tab-pane>
      <el-tab-pane label="网站设置">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form label-width="170px" style="margin-top: 30px" :model="enterpriseData" v-loading=ent_loading element-loading-text="修改中">
              <el-form-item label="系统名称">
                <el-col :span="20">
                  <el-input v-model="enterpriseData.url_name"></el-input>
                </el-col>
                <el-col :span="2" align="center">
                  <el-tooltip content="自定义系统名称" placement="top">
                    <i class="el-icon-question"></i>
                  </el-tooltip>
                </el-col>
              </el-form-item>
              <el-form-item label="系统LOGO（建议尺寸:289 × 66）">
                <el-col :span="20" style="margin-top: 15px">
                  <el-upload
                    class="avatar-uploader"
                    action=""
                    :http-request="uploadlogo"
                    :show-file-list="false"
                    :before-upload="beforeAvatarUpload">
                    <img v-if="enterpriseData.enterprise_logo" :src="enterpriseData.enterprise_logo" class="avatar">
                    <i v-else class="el-icon-plus avatar-uploader-icon"></i>
                  </el-upload>
                </el-col>
                <el-col :span="2" align="center">
                  <el-tooltip content="自定义登录页LOGO（建议尺寸:289 × 66）" placement="top">
                    <i class="el-icon-question"></i>
                  </el-tooltip>
                </el-col>
              </el-form-item>
              <el-form-item label="系统登录背景图（建议尺寸:1920 × 1080）">
                <el-col :span="20" style="margin-top: 15px">
                  <el-upload
                    class="avatar-uploader"
                    action=""
                    :http-request="uploadbg"
                    :show-file-list="false"
                    :before-upload="beforeAvatarUpload2">
                    <img v-if="enterpriseData.enterprise_bg" :src="enterpriseData.enterprise_bg" class="avatar">
                    <i v-else class="el-icon-plus avatar-uploader-icon"></i>
                  </el-upload>
                </el-col>
                <el-col :span="2" align="center">
                  <el-tooltip content="自定义系统背景图（建议尺寸:1920 × 1080）" placement="top">
                    <i class="el-icon-question"></i>
                  </el-tooltip>
                </el-col>
              </el-form-item>
              <el-form-item>
                <el-button type="primary" @click="settingEnterpriseUpdate">修改</el-button>
                <el-button @click="resetSetting">重置</el-button>
              </el-form-item>
            </el-form>
          </el-col>
        </el-row>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script>
  import { settingGet,settingUpdate,enterpriseUpdate } from "@/api/setting"
  import { uploadImage } from '@/api/layout'
  export default {
    inject: ['reload'],
    name: 'setting',
    data() {
      return {
        loading: false,
        ent_loading: false,
        data: {
          tabPosition:'left',
          share_username: '',
          username: '',
          pwd: '',
          time: '1800',
          is_synchronization: false,
          del_container:true,
          cancel_validation:false,
          cancel_registration:false,
        },
        enterpriseData:{
          url_name:"",
          enterprise_logo:"",
          enterprise_bg:""
        },
        newLogoFile: new FormData(),
        newBgFile: new FormData(),
        dialogImageUrl: '',
        dialogVisible: true,
        disabled: true
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
            this.enterpriseData = rspData.data
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
        formData.set("is_synchronization",this.data.is_synchronization)
        formData.set("del_container",this.data.del_container)
        formData.set("cancel_validation",this.data.cancel_validation)
        formData.set("cancel_registration",this.data.cancel_registration)
        this.loading = true
        settingUpdate(formData).then(response => {
          let rspData = response.data
          this.loading = false
          if(rspData.status === 200){
            this.data = rspData.data
            this.$message({
              message: '修改成功',
              type: "success",
            })
          }else{
            this.$message({
              message: rspData.msg,
              type: "error",
            })
          }
        })
      },
      settingEnterpriseUpdate(){
        let formData = new FormData()
        formData.set("url_name",this.enterpriseData.url_name)
        formData.set("enterprise_bg",this.enterpriseData.enterprise_bg)
        formData.set("enterprise_logo",this.enterpriseData.enterprise_logo)
        this.ent_loading = true
        enterpriseUpdate(formData).then(response => {
          let rspData = response.data
          this.ent_loading = false
          if(rspData.status === 200){
            this.data = rspData.data
            this.$message({
              message: '修改成功',
              type: "success",
            })
          }else{
            this.$message({
              message: rspData.msg,
              type: "error",
            })
          }
        })
      },
      beforeAvatarUpload(file){
        let isType = file.type === 'image/jpeg' || file.type === 'image/png';
        let isSize = file.size / 1024 /1024 < 2;
        this.newLogoFile = new FormData()
        if (!isType){
          return this.$message.error("只能上传jpg/png图片")
        }
        else if (!isSize){
          return this.$message.error("图片大小不能超过2M")
        }
        else if (file){
          this.newLogoFile.set("img", file)
        }else{
          return false;
        }
      },
      beforeAvatarUpload2(file){
        let isType = file.type === 'image/jpeg' || file.type === 'image/png';
        let isSize = file.size / 1024 /1024 < 2;
        this.newBgFile = new FormData()
        if (!isType){
          return this.$message.error("只能上传jpg/png图片")
        }
        else if (!isSize){
          return this.$message.error("图片大小不能超过2M")
        }
        else if (file){
          this.newBgFile.set("img", file)
        }else{
          return false;
        }
      },
      uploadlogo(){
        let data = this.newLogoFile
        if (!data){
          this.$message({
              message: '上传失败',
              type: 'success'
            })
        }else {
        uploadImage(data).then(response => {
          let rsp = response.data
          if (rsp.data && rsp.status === 200){
            this.$message({
              message: '上传成功',
              type: 'success'
            })
            this.enterpriseData.enterprise_logo = '/images/' + rsp.data
          }else{
            this.$message({
              message: rsp.msg,
              type: 'error'
            })
          }
        }).catch(err => {
          this.$message({
            message: "服务器内部错误",
            type: 'error'
          })
        })
      }},
      uploadbg(){
        let data = this.newBgFile
        if (!data){
          this.$message({
              message: '上传失败',
              type: 'success'
            })
        }else {
        uploadImage(data).then(response => {
          let rsp = response.data
          if (rsp.data && rsp.status === 200){
            this.$message({
              message: '上传成功',
              type: 'success'
            })
            this.enterpriseData.enterprise_bg = '/images/' + rsp.data
          }else{
            this.$message({
              message: rsp.msg,
              type: 'error'
            })
          }
        }).catch(err => {
          this.$message({
            message: "服务器内部错误",
            type: 'error'
          })
        })
      }},
      resetSetting() {
        let formData = new FormData()
        formData.set("url_name", "")
        formData.set("enterprise_bg", "")
        formData.set("enterprise_logo", "")
        this.ent_loading = true
        enterpriseUpdate(formData).then(response => {
          let rspData = response.data
          this.ent_loading = false
          if (rspData.status === 200) {
            this.data = rspData.data
            this.$message({
              message: '重置成功',
              type: "success",
            })
            this.reload()
          } else {
            this.$message({
              message: rspData.msg,
              type: "error",
            })
          }
        })
      }
    }
  }
</script>

<style>
  .avatar-uploader .el-upload {
  border: 1px dashed #d9d9d9;
  border-radius: 6px;
  cursor: pointer;
  position: relative;
  overflow: hidden;
}
.avatar-uploader .el-upload:hover {
  border-color: #409EFF;
}
.avatar-uploader-icon {
  font-size: 28px;
  color: #8c939d;
  width: 330px;
  height: 178px;
  line-height: 178px;
  text-align: center;
}
.avatar {
  width: 330px;
  height: 178px;
  display: block;
}
</style>


<style scoped>
.relationContainer{
  display:flex;
  justify-content:center;/*主轴上居中*/
  align-items:flex-end;/*侧轴上居中*/

}
</style>
