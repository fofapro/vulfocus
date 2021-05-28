<template>
  <div style="width: 100%" class="app-container">
    <div class="svgHeadItemLst svgToolBarItem">
        <el-button size="small" style="margin: 3px;" type="primary" @click="saveTopoJson">创建计时模版
        </el-button>
    </div>
    <el-dialog :visible.sync="editShow" title="创建">
      <el-form label-width="150px" v-loading="editLoading" element-loading-text="创建中">
        <el-form-item label="计时时间" :label-width="formLabelWidth">
          <el-select v-model="form.time_range" placeholder="请选择时间范围" size="medium" >
            <el-option label="30分钟" value="30"></el-option>
            <el-option label="60分钟" value="60"></el-option>
            <el-option label="90分钟" value="90"></el-option>
            <el-option label="120分钟" value="120"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="模版描述" :label-width="formLabelWidth" >
          <el-input type="textarea" v-model="form.desc" autocomplete="off" :autosize="{ minRows: 4, maxRows: 6}" ></el-input>
        </el-form-item>
        <el-form-item label="Banner 图" :label-width="formLabelWidth">
          <el-upload
            class="avatar-uploader"
            action=""
            :http-request="upload"
            :show-file-list="false"
            :before-upload="beforeAvatarUpload">
            <img v-if="form.imageName" :src="form.imageName" class="avatar">
            <i v-else class="el-icon-plus avatar-uploader-icon"></i>
          </el-upload>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleCreate()">创建</el-button>
          <el-button type="primary" @click="handleCancel">取消</el-button>
        </el-form-item>
      </el-form>
    </el-dialog>
    <el-table :data="tableData" border stripe style="width: 100%;margin-top:20px;">
      <el-table-column prop="temp_id" label="id" width="300"></el-table-column>
      <el-table-column prop="time_range" label="时间范围" width="180"></el-table-column>
      <el-table-column prop="time_desc" label="描述"></el-table-column>
      <el-table-column fixed="right" label="操作" width="100">
        <template slot-scope="{row}">
          <el-button type="text" size="small" @click='handleDelete(row)'>删除</el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>


<script>
  import { timetemplist,timetempadd,timetempdelete } from '@/api/timemoudel'
  import { uploadImage } from '@/api/layout'
  export default {
    inject:['reload'],
    data() {
      return {
        formLabelWidth:"100px",
        tableData: [],
        loading: false,
        form: {
          time_range:'',
          desc: '',
          imageName: '',
        },
        flag:"temp",
        editShow: false,
        editLoading: false,
        newFile: new FormData()
      };
    },
    created(){
      this.templist()
    },
    methods: {
      templist(){
        timetemplist(this.flag).then(response =>{
          let data = response.data.results
          console.log(data)
          this.tableData = data
          })
       },
      handleCreate(){
        let imageName = this.form.imageName.replace(process.env.VUE_APP_BASE_API + '/static/', "")
        let formData = new FormData()
        formData.set("time_range", this.form.time_range)
        formData.set("desc", this.form.desc)
        formData.set("imageName", imageName)
        console.log(formData)
        timetempadd(formData).then(response => {
          let rsDta = response.data
          if (rsDta.status === 200){
            this.$message({
              type: 'success',
              message: '创建成功'
            })
          }else{
            this.$message({
            type: 'error',
            message: rsDta.message,
          })
          }
          this.reload()
        })
      },
      saveTopoJson() {
        this.editShow = true
      },
      handleCancel(){
        this.editShow = false
      },
      beforeAvatarUpload(file){
        if (file){
          this.newFile.set("img", file)
        }else{
          return false;
        }
      },
      upload(){
        let data = this.newFile
        uploadImage(data).then(response => {
          let rsp = response.data
          console.log(rsp,1111111)
          if (rsp.data && rsp.status === 200){
            this.$message({
              message: '上传成功',
              type: 'success'
            })
            this.form.imageName = process.env.VUE_APP_BASE_API + '/static/' + rsp.data
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
      },
      handleDelete(row){
        timetempdelete(row.temp_id).then(response => {
          let data = response.data
          if (data.code === 200){
            this.$message({
              type:'success',
              message: data.message
            })
          }else{
            this.$message({
              type:'error',
              message: data.message
            })
          }
          this.reload()
        })
      }
    }
  }
</script>

<style scoped>
.avatar-uploader .el-upload {
  border: 1px dashed #d9d9d9;
  border-radius: 6px;
  cursor: pointer;
  position: relative;
  overflow: hidden;
}
.avatar-uploader .el-upload:hover {
  border-color: #409eff;
}
.avatar-uploader-icon {
  font-size: 28px;
  color: #8c939d;
  width: 120px;
  height: 120px;
  line-height: 120px;
  text-align: center;
}
.avatar {
  width: 120px;
  height: 120px;
  display: block;
}
.el-collapse-item__header {
  -webkit-user-select: none;
  user-select: none;
  /*-moz-select: none;*/
  /*-ms-select: none;*/
  /*-o-select: none;*/
}

</style>
