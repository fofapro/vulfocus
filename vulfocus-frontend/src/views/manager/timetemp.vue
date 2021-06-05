<template>
  <div style="width: 100%" class="app-container">
    <div class="svgHeadItemLst svgToolBarItem">
        <el-button size="small" style="margin: 3px;" type="primary" @click="saveTopoJson">创建计时模版
        </el-button>
    </div>
    <div>
      <el-dialog :visible.sync="editShow" title="创建" width="50%" >
        <div style="display: flex;justify-content: flex-start;">
          <el-steps :active="index" direction="vertical">
            <el-step title="时间信息" size="mini"></el-step>
            <el-step title="漏洞类型"></el-step>
            <el-step title="Rank范围"></el-step>
          </el-steps>
          <div style="margin-left: 30px;display: flex;justify-content: center;align-items: center;width: 80%;">
            <div v-show="index===0" style="width: 500px">
              <el-form v-loading="editLoading" element-loading-text="创建中" @keyup.enter.native="next" >
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
      </el-form>
            </div>
            <div v-show="index===1" style="width: 500px" >
              <el-select v-model="form.time_img_type" multiple filterable allow-create default-first-option placeholder="请选择镜像标签" >
                <el-option v-for="item in degreeList" :key="item.value" :label="item.label" :value="item.value"> </el-option>
              </el-select>
            </div>
            <div v-show="index===2" style="width: 500px;">
              <el-input-number v-model="form.rank_range" :precision="1" :step="0.5" :max="5" :min="0"></el-input-number>
            </div>
          </div>
        </div>
        <div style="display: flex;align-items: center;justify-content: center;padding: 0px;margin: 0px;">
          <el-button round size="mini" v-if="index!==0" @click="index--">上一步</el-button>
          <el-button type="primary" round size="mini" @click="next" v-text="index===2?'完成':'下一步'"></el-button>
        </div>
      </el-dialog>
    </div>
    <el-table :data="tableData" border stripe style="width: 100%;margin-top:20px;">
      <el-table-column prop="temp_id" label="id" width="300"></el-table-column>
      <el-table-column prop="time_range" label="时间范围" width="180"></el-table-column>
      <el-table-column prop="time_desc" label="描述"></el-table-column>
      <el-table-column label="漏洞类型">
        <template slot-scope="{row}" v-if="row.time_img_type !==''">
          <el-tag v-for="i in row.time_img_type">{{i}}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="rank_range" label="Rank范围"></el-table-column>
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
        Donelabs: "开始",
        index:0,
        formLabelWidth:"100px",
        tableData: [],
        loading: false,
        form: {
          time_range:'',
          desc: '',
          imageName: '',
          time_img_type:[],
          rank_range:0
        },
        degreeList:[
          {value:"命令执行", lable:"命令执行"},
          {value:"代码执行", lable:"代码执行"},
          {value:"文件写入", lable:"文件写入"},
          {value:"文件上传", lable:"文件上传"},
          {value:"后门", lable:"后门"},
          {value:"默认口令", lable:"默认口令"},
          {value:"弱口令", lable:"弱口令"},
          {value:"权限绕过", lable:"权限绕过"},
          {value:"未授权访问", lable:"未授权访问"},
          {value:"XXE漏洞", lable:"XXE漏洞"},
          {value:"SQL注入", lable:"SQL注入"},
          {value:"文件读取", lable:"文件读取"},
          {value:"文件下载", lable:"文件下载"},
          {value:"文件包含", lable:"文件包含"},
          {value:"文件删除", lable:"文件删除"},
          {value:"目录遍历", lable:"目录遍历"},
          {value:"信息泄漏", lable:"信息泄漏"},
          {value:"任意账户操作", lable:"任意账户操作"},
          {value:"XSS漏洞", lable:"XSS漏洞"},
          {value:"SSRF漏洞", lable:"SSRF漏洞"},
          {value:"CSRF漏洞", lable:"CSRF漏洞"},
        ],
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
          this.tableData = data
          })
       },
      handleCreate(){
        let imageName = this.form.imageName.replace('/images/', "")
        let formData = new FormData()
        formData.set("time_range", this.form.time_range)
        formData.set("desc", this.form.desc)
        formData.set("imageName", imageName)
        formData.set("rank_range", this.form.rank_range)
        formData.set("time_img_type", this.form.time_img_type)
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
          if (rsp.data && rsp.status === 200){
            this.$message({
              message: '上传成功',
              type: 'success'
            })
            this.form.imageName = '/images/' + rsp.data
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
      },
      next(){
        var _this = this;
        if (this.index === 2) {
          this.handleCreate()
        } else {
          this.index++;
        }
      },
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
