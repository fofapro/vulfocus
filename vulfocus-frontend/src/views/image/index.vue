<template>
  <div class="app-container">
      <el-dialog :visible.sync="centerDialogVisible"width="60%">
        <el-tabs type="border-card">
          <el-tab-pane label="添加">
            <el-form label-width="80px"
                     v-loading="loading"
                     element-loading-text="添加中">
              <el-form-item label="漏洞名称">
                <el-input v-model="vulInfo.vul_name" size="medium"></el-input>
              </el-form-item>
              <el-form-item label="镜像">
                <el-col :span="17">
                  <el-upload
                    v-if="imgType === 'file'"
                    ref="upload"
                    :http-request="uploadImg"
                    accept=".tar"
                    action="/CombinationImage/"
                    :limit="1"
                    :auto-upload="false">
                    <el-button slot="trigger" size="medium" type="primary">选取文件</el-button>
                  </el-upload>
                  <el-autocomplete style="width: 100%"  v-model="vulInfo.name" v-if="imgType === 'text'" size="medium"
                                   :fetch-suggestions="querySearchAsync" @select="handleSelect"></el-autocomplete>
                </el-col>
                <el-col :span="5" style="float: right; right: 0;">
                  <el-button v-model="imgType" @click.stop="changeType" size="medium">{{imgTypeText}}</el-button>
                </el-col>
              </el-form-item>
              <el-form-item label="Rank">
                <el-input-number v-model="vulInfo.rank" :min="0.5" :max="5.0" :precision="1" :step="0.5" size="medium"></el-input-number>
              </el-form-item>
              <el-form-item label="描述">
                <el-input type="textarea" v-model="vulInfo.desc" size="medium"></el-input>
              </el-form-item>
              <el-form-item>
                <el-button type="primary"  @click="uploadImg" size="medium">提 交</el-button>
              </el-form-item>
            </el-form>
          </el-tab-pane>
          <el-tab-pane label="本地导入">配置管理</el-tab-pane>
          <el-tab-pane label="批量下载">角色管理</el-tab-pane>
        </el-tabs>
    </el-dialog>
    <div class="filter-container">
      <el-input v-model="search" style="width: 230px;" size="medium"></el-input>
      <el-button class="filter-item" size="medium" style="margin-left: 10px;margin-bottom: 10px" type="primary" icon="el-icon-search" @click="handleQuery">
        查询
      </el-button>
      <el-button class="filter-item" size="medium" style="margin-left: 10px;margin-bottom: 10px" type="primary" icon="el-icon-edit" @click="openCreate">
        添加
      </el-button>
    </div>
    <el-table
      :data="tableData"
      border
      stripe
      align = "center"
      style="width: 100%">
      <el-table-column
        type="index"
        width="50">
      </el-table-column>
      <el-table-column
        prop="image_name"
        label="镜像名称"
        :show-overflow-tooltip=true
        width="220">
      </el-table-column>
      <el-table-column
        prop="image_vul_name"
        label="漏洞名称"
        :show-overflow-tooltip=true
        width="180">
      </el-table-column>
      <el-table-column
        prop="image_port"
        label="端口"
        width="100">
      </el-table-column>
      <el-table-column
        prop="rank"
        label="分数"
        width="50">
      </el-table-column>
      <el-table-column
        prop="image_desc"
        :show-overflow-tooltip=true
        label="描述"
        width="340">
      </el-table-column>
      <el-table-column
        fixed="right"
        label="操作"
        width="220">
        <template slot-scope="{row}">
<!--          <el-tag effect="dark" type="danger" v-if="row.is_ok === false && row.status.task_id === ''"><i class="el-icon-switch-button"></i>镜像不存在</el-tag>-->
<!--          <el-tag effect="dark" v-else-if="row.is_ok === false && row.status.task_id !== ''"><i class="el-icon-loading"></i>下载中</el-tag>-->
          <el-tag effect="dark" v-if="row.is_ok === false"><i class="el-icon-loading"></i>下载中</el-tag>
<!--          || (row.is_ok === false && row.status.task_id === '')-->
          <el-button
            v-if="(row.is_ok === true)"
            size="mini"
            type="danger"
            icon="el-icon-delete"
            @click="handleDelete(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script>
  import { ImgList } from "@/api/docker"
  import { search } from "@/api/utils"
  import { ImageAdd, ImageDelete } from "@/api/image"
  import { getTask,batchTask } from '@/api/tasks'


  export default {
    name: 'index',
    data() {
      return {
        tableData: [],
        search: "",
        centerDialogVisible: false,
        startCon: false,
        vulInfo: {
          rank: "",
          name: "",
          vul_name: "",
          desc: "",
        },
        imgType: "text",
        imgTypeText: "切换为文件",
        loading: false,
        summaries:[],
        taskCheckInterval :null,
        tmpImageNameList:[]
      //  image_id
      }
    },
    created() {
      this.initTableData()
      this.initSummariesList()
      // this.checkTaskStatus()
    },
    methods:{
      querySearchAsync(queryString, cb) {
        let restaurants = this.summaries
        if (queryString === null || queryString === "" || queryString.length === 0){
          this.initSummariesList()
          cb(restaurants);
        }else{
          search(queryString).then(response => {
            this.summaries = []
            if(response.status === 200){
              let summariesList = response.data["summaries"]
              if (summariesList != null){
                summariesList.forEach((item, index, arr) => {
                  this.summaries.push({"value": item["name"]})
                })
              }
              restaurants = this.summaries
              cb(restaurants);
            }
          })
        }
      },
      searchSummariesList(keyword){
        this.summaries = []
        search(keyword).then(response => {
          this.summaries = []
          if(response.status === 200){
            let summariesList = response.data["summaries"]
            summariesList.forEach((item, index, arr) => {
              this.summaries.push({"value": item["name"]})
            });
          }
        })
      },
      initSummariesList(){
        this.searchSummariesList("")
      },
      initTableData(){
        clearInterval(this.taskCheckInterval)
        ImgList(undefined, true).then(response => {
          this.tableData = response.data
          let tmpTableData = response.data
          this.taskCheckInterval = window.setInterval(() => {
            setTimeout(()=>{
              let taskList = []
              taskList = this.checkTask(tmpTableData)
              if (taskList == null || taskList.length === 0){
                clearInterval(this.taskCheckInterval)
              }
            },0)
          },5000)
        })
      },
      openCreate(){
        this.centerDialogVisible = true
        this.vulInfo.rank = 2.5
        this.vulInfo.name = ""
        this.vulInfo.vul_name = ""
        this.vulInfo.desc = ""
      },
      changeType(){
        if(this.imgType === 'file'){
          this.imgType = 'text'
          this.imgTypeText = "切换为文件"
        }else{
          this.imgType = 'file'
          this.imgTypeText = "切换为文本"
        }
      },
      uploadImg(fileObj) {
        let formData = new FormData()
        if (this.$refs.upload != null){
          let uploadFiles = this.$refs.upload.uploadFiles
          if (this.$refs.upload.uploadFiles != null || this.$refs.upload.uploadFiles.length > 0){
            formData.set("file", uploadFiles[0].raw);
          }
        }
        formData.set("rank", this.vulInfo.rank)
        formData.set("image_name", this.vulInfo.name)
        formData.set("image_vul_name", this.vulInfo.vul_name)
        formData.set("image_desc", this.vulInfo.desc)
        this.loading = true
        ImageAdd(formData).then(response => {
          this.loading = false
          let data = response.data
          let msg = data["data"]
          if(msg != null && (msg.indexOf("成功") > -1 || msg.indexOf("失败") > -1 )){
            let tmpMsg = msg.replace("拉取镜像", "").replace("任务下发成功", "").replace(" ", "")
            this.tmpImageNameList.push(tmpMsg)
            console.log(this.tmpImageNameList)
            if(msg.indexOf("成功") > -1 ){
              this.$message({
                message: msg,
                type: "success",
              })
              this.centerDialogVisible = false
              this.initTableData()
            }else{
              this.$message({
                message: msg,
                type: "error",
                duration: 3 * 1000
              })
              this.centerDialogVisible = false
            }
          }else{
            this.$message({
              message: data["msg"],
              type: "success",
              duration: 3 * 1000
            })
            this.centerDialogVisible = false
            this.initTableData()
          }
        })
      },
      handleDelete(row){
        this.$confirm('确认删除?', '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        }).then(() => {
          ImageDelete(row.image_id).then(response => {
            let data = response.data
            if(data.status === 200){
              this.$message({
                type: 'success',
                message: '删除成功!'
              })
              this.initTableData()
            }else{
              this.$message({
                type: 'error',
                message: data.msg
              });
            }
          })
        }).catch(() => {
        });
      },
      handleQuery(){
        ImgList(this.search, true).then(response => {
          this.tableData = response.data
        })
      },
      handleSelect(item){
        this.vulInfo.name = item.value
        this.vulInfo.vul_name = item.value.replace("vulfocus/", "")
        this.vulInfo.desc = item.value.replace("vulfocus/", "")
      },
      checkTask(tableData){
        let taskList = []
        let taskDict = {}
        tableData.forEach((item, index, arr) => {
          let isOk = item["is_ok"]
          let taskId = item["status"]["task_id"]
          let image_name = item.image_name
          if ((isOk === false && taskId != null && taskId !== "")){
            taskList.push(taskId)
            taskDict[taskId] = item
          }
          if(this.tmpImageNameList.indexOf(image_name) > 0){
            this.$message({
              message: taskMsg["data"]["msg"],
              type: "success",
            })
            this.removeArray(this.tmpImageNameList, image_name)
          }
        })
        let taskIdStr = taskList.join(",")
        if(taskIdStr != null && taskIdStr !== ""){
          let formData = new FormData()
          formData.set("task_ids", taskIdStr)
          batchTask(formData).then(response => {
            let data = response.data.data
            for(let key in data){
              let taskMsg = data[key]
              let status = taskMsg["status"]
              if(status !== 1){
                this.removeArray(taskList, key)
                taskDict[key].is_ok = true
                if(taskMsg["data"]["status"] === 200){
                  this.$message({
                    message: taskMsg["data"]["msg"],
                    type: "success",
                  })
                }else{
                  this.$message({
                    message: taskMsg["data"]["msg"],
                    type: "error",
                  })
                }
              }
            }
          })
        }
        return taskList
      },
      removeArray(taskList,val){
        for(let i = 0; i < taskList.length; i++) {
          if(taskList[i] == val) {
            taskList.splice(i, 1);
            break;
          }
        }
      }
    }
  }
</script>

<style scoped>

</style>
