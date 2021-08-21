<template>
  <div>
    <el-card style="margin-bottom:20px;">
      <div slot="header" class="clearfix">
        <span>About me</span>
      </div>
      <div class="user-profile">
        <div class="box-center">
          <el-upload
            class="upload_img"
            action=""
            :http-request="upload"
            :show-file-list="false"
            :before-upload="beforeAvatarUpload">
            <pan-thumb :image="user.avatar" :height="'100px'" :width="'100px'" :hoverable="false">
              <div>Hello</div>
              {{ user.role }}
            </pan-thumb>
          </el-upload>
        </div>
        <div class="box-center" >
          <div class="user-name text-center">{{ user.name }}</div>
          <div class="user-role text-center text-muted">{{ user.role  }}</div>
        </div>
      </div>
      <div class="user-bio">
        <div class="user-education user-bio-section">
          <div class="user-bio-section-header"><svg-icon icon-class="education" /><span> 积分：{{user.rank}}</span></div>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script>
import PanThumb from '@/components/PanThumb'
import {uploaduserimgae} from '@/api/user'
export default {
  components: { PanThumb },
  props: {
    user: {
      type: Object,
      default: () => {
        return {
          name: '',
          email: '',
          avatar: '',
          roles: '',
            rank:'',
        }
      }
    }
  },
  data() {
    return {
      newFile: new FormData(),
    }
  },
  methods : {
    beforeAvatarUpload(file){
      if(file){
        this.newFile.set("img",file)
      }
      else
        return false
    },
    upload(){
      uploaduserimgae(this.newFile).then(response=>{
        let data = response.data;
        if(data.code===200 && data.msg === "上传成功"){
          this.$message({
            message: '上传成功',
            type: 'success'
          })
          location.reload();
          this.box_show=false;
        }
        if (data.code===400){
          this.$message({
            message: data.msg,
            type: 'error'
          })
        }
      })
    }
  }
}
</script>

<style lang="scss" scoped>
 .avatar-uploader {
   border: 1px dashed #d9d9d9;
   border-radius: 6px;
   cursor: pointer;
   position: relative;
   overflow: hidden;
 }
 .avatar-uploader-icon {
  font-size: 28px;
  color: #8c939d;
  width: 120px;
  height: 120px;
  line-height: 120px;
  text-align: center;
  }

 .box-center {
   margin: 0 auto;
   display: table;
 }

 .text-muted {
   color: #777;
 }

 .user-profile {
   .user-name {
     font-weight: bold;
   }

   .box-center {
     padding-top: 10px;
   }

   .user-role {
     padding-top: 10px;
     font-weight: 400;
     font-size: 14px;
   }

   .box-social {
     padding-top: 30px;

     .el-table {
       border-top: 1px solid #dfe6ec;
     }
   }

   .user-follow {
     padding-top: 20px;
   }
 }

 .user-bio {
   margin-top: 20px;
   color: #606266;

   span {
     padding-left: 4px;
   }

   .user-bio-section {
     font-size: 14px;
     padding: 15px 0;

     .user-bio-section-header {
       border-bottom: 1px solid #dfe6ec;
       padding-bottom: 10px;
       margin-bottom: 10px;
       font-weight: bold;
     }
   }
 }
</style>
