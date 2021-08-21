<template>
  <div class="container">
    <div class="widget">
      <el-tabs type="border-card" v-loading='loading' element-loading-text="正在安装相关镜像"
               element-loading-spinner="el-icon-loading"
               element-loading-background="rgba(0, 0, 0, 0.1)" >
        <el-tab-pane id="ceshi">
          <span slot="label"><i class="el-icon-document"></i>DockerCompose</span>
          <el-form :model=composeForm inline ref="build" size="mini" :rules="rules">
            <el-form-item label="名称" prop="tag1">
              <el-input v-model="composeForm.tag1" placeholder="eg. redis:latest"></el-input>
            </el-form-item>
<!--            <el-form-item label="分类">-->
<!--              <el-select v-model="composeForm.degree" style="width: 300px" multiple filterable allow-create default-first-option placeholder="请选择镜像标签" >-->
<!--                <el-option v-for="item in degreeList" :key="item.value" :label="item.label" :value="item.value"> </el-option>-->
<!--              </el-select>-->
<!--            </el-form-item>-->
            <el-form-item label="Rank">
              <el-input-number v-model="composeForm.rank" :min="0.0" :max="5.0" :precision="1" :step="0.5" size="mini"></el-input-number>
              <el-tooltip content="默认分数为2.5分，可根据漏洞的利用难度进行评判" placement="top">
                <i class="el-icon-question"></i>
              </el-tooltip>
            </el-form-item>
            <el-form-item label="flag">
              <el-switch v-model="composeForm.is_flag"></el-switch>
              <el-tooltip content="是否开启flag" placement="top">
                <i class="el-icon-question"></i>
              </el-tooltip>
            </el-form-item>
          </el-form>
          <el-tabs value="dockerfile" ref="tab">
            <el-tab-pane name="dockerfile">
              <span slot="label"><i class="el-icon-edit"></i> DockerCompose.yml</span>
              <div>
                <el-form>
                  <el-form-item>
                    <el-input v-model="compose_content" type="textarea" rows="10"
                              placeholder="Define or paste the content of Your DockerCompose.yml here"></el-input>
                  </el-form-item>
                </el-form>
              </div>
            </el-tab-pane>
          </el-tabs>
          <div>
            <el-row>
              <el-col :span="2">
                <div class="action-group">
                  <el-button @click="compose_build" type="primary" size="mini">编译</el-button>
                </div>
              </el-col>
              <el-col :span="22" style="margin-top: 10px">
                <div>
                  <el-upload
                    ref="upload"
                    :http-request="upload"
                    :max-size="2048"
                    action="/CombinationImage/"
                    :before-upload="beforeAvatarUpload"
                    :on-remove="removeChange"
                    :on-change="handleChange"
                    :file-list="fileList">
                    <el-button slot="trigger" style="margin-bottom: 20px" size="mini" type="primary">上传文件</el-button>
                  </el-upload>
                </div>
              </el-col>
            </el-row>
          </div>
        </el-tab-pane>
      </el-tabs>
    </div>
  </div>
</template>

<script>
import { build_compose,show_build_status,uploadFile,deleteFile } from "@/api/layout"
import { getTask,batchTask,progressTask } from '@/api/tasks'

export default {
  inject: ['reload'],
  data() {
    return {
      rules: {
        tag: [
          {required: true, max: 100, min: 2, message: "请输入要构建的镜像名称"}
        ],
        tag1:[
          {required: true, max: 100, min: 2, message: "请输入要构建的镜像名称"}
        ]
      },
      selectHub: 'DockerHub',
      imageName: '',
      buildForm: {
        tag: '',
      },
      composeForm:{
        tag1:'',
        rank:'',
        degree:[],
        is_flag:true
      },
      options: [{
        value: 'DockerHub',
        label: 'DockerHub'
      }],
      file: null,
      output: [],
      pk: null,
      content: '',
      compose_content:"",
      listTotal: 0,
      listData: [],
      showLog: false,
      loading: false,
      newFile: new FormData(),
      fileList:[],
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
    }
  },
  created() {
    // this.showCompose()
  },
  methods:{
    showCompose(){
      show_build_status().then(response=>{
        if (response.data.code === 200){
          let data = response.data['data']
          let img_name = response.data['img_name']
          this.compose_content = data
          this.composeForm.tag1 = img_name
          this.loading = true
        }else {
        }
      })
    },
    removeChange(file,fileList) {
      this.$confirm('此操作将永久删除该文件, 是否继续?', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        let delFile = new FormData()
        delFile.set("file", file.name)
        deleteFile(delFile).then(response=>{
          let data = response.data
          if (data.status === 200){
            for (let i=0; i<fileList.length; i++){
              if (fileList[i] === file){
                fileList.splice(i,1)
              }
            }
            this.$message({
              type: 'success',
              message: '删除成功!'
            });
          }else {
            fileList.push(file)
            this.$message({
              type: 'error',
              message: '删除失败!'
            });
          }
        })
      }).catch(() => {
        fileList.push(file)
        this.$message({
          type: 'info',
          message: '已取消删除'
        });
      });
    },
    compose_build(){
      let data = {}
      data.compose_content = this.compose_content
      data.tag = this.composeForm.tag1
      data.rank = this.composeForm.rank
      data.degree = this.composeForm.degree
      data.is_flag = this.composeForm.is_flag
      build_compose(data).then(response=>{
        if (response.data.code === 200){
          this.$message({
            title: '构建任务创建成功',
            message: response.data.message,
            type: 'success'
          });
          this.reload()
        }else {
          this.$message({
            title: '构建任务创建失败',
            message: response.data.message,
            type: 'error'
          });
        }
      })
    },
    beforeAvatarUpload(file){
      if (file){
        this.newFile.set("file", file)
      }else{
        return false;
      }
    },
    handleChange(file,fileList){
      this.fileList = fileList
    },
    upload(file,fileList){
      let size = file.file.size /1024 /1024
      if (size>2){
        this.$message({
          message: "文件大小必须小于2M",
          type: 'error'
        })
        this.fileList.pop()
      }else{
        let data = this.newFile
        uploadFile(data).then(response => {
          let rsp = response.data
          if (rsp.data && rsp.status === 200){
            for (let i=0; i<this.fileList.length; i++){
                if (this.fileList[i].name.indexOf("../compose_file/")===-1){
                  this.fileList[i].name = "../compose_file/" + this.fileList[i].name
                }else {
                }
            }
            this.$message({
              message: '上传成功',
              type: 'success'
            })
          }else{
            this.fileList.pop()
            this.$message({
              message: rsp.msg,
              type: 'error'
            })
          }
        }).catch(err => {
          this.fileList.pop()
          this.$message({
            message: "服务器内部错误",
            type: 'error'
          })
        })
      }
    },
  }
}
</script>

<style scoped>
.small {
  font-size: 80%;
}
.btn-group svg {
  width: 14px;
  height: 14px;
  margin-right: 4px;
}
.wd-title {
  padding: 10px 6px;
  color: #777;
  border-bottom: 1px solid #777;
}
.action-group {
  padding: 10px 6px;
}
.pre {
  padding: 0 15px;
  color: #000;
  font-size: 13px;
  border: 1px solid #ccc;
  border-radius: 4px;
}
.line {
  margin-block-start: 2px;
  margin-block-end: 2px;
}
</style>
