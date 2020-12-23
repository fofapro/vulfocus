<template>
  <div class="app-container">
    <el-dialog :visible.sync="centerDialogVisible" title="添加" width="60%">
        <el-tabs value="add" @tab-click="handleClick">
          <el-tab-pane name="add" label="添加">
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
                &nbsp;&nbsp;&nbsp;
                <el-tooltip content="默认分数为2.5分，可根据漏洞的利用难度进行评判" placement="top">
                  <i class="el-icon-question"></i>
                </el-tooltip>
              </el-form-item>
              <el-form-item label="描述">
                <el-input type="textarea" v-model="vulInfo.desc" size="medium"></el-input>
              </el-form-item>
              <el-form-item>
                <el-button type="primary"  @click="uploadImg" size="medium">提 交</el-button>
              </el-form-item>
            </el-form>
          </el-tab-pane>
          <el-tab-pane name="local" label="本地导入">
            <div class="filter-container">
              <el-input v-model="localSearch" style="width: 230px;" size="medium"></el-input>
              <el-button class="filter-item" size="medium" style="margin-left: 10px;margin-bottom: 10px" type="primary" icon="el-icon-circle-plus-outline" @click="batchLocalAdd">
                一键导入
              </el-button>&nbsp;&nbsp;&nbsp;
              <el-tooltip content="一键导入默认导入分数为 2.5 分,漏洞名称为镜像名称,漏洞描述为漏洞名称" placement="top">
                <i class="el-icon-question"></i>
              </el-tooltip>
            </div>
            <el-table :data="localImageList.filter(data => !localSearch || data.name.toLowerCase().includes(localSearch.toLowerCase()))" @selection-change="handleSelectLocalImages" tooltip-effect="dark" style="width: 100%" v-loading="localLoading">
              <el-table-column type="selection" width="55"></el-table-column>
              <el-table-column prop="name" label="名称" :show-overflow-tooltip=true> </el-table-column>
              <el-table-column label="标签" width="120">
                <template slot-scope="{row}">
                  <el-tag v-if="row.flag===true" effect="dark" type="info">已导入</el-tag>
                  <el-tag v-else-if="row.flag===false" effect="dark">未导入</el-tag>
                </template>
              </el-table-column>
              <el-table-column fixed="right" label="操作" width="120">
                <template slot-scope="{row}">
                  <el-button @click.native.prevent="handleLocalRemove(row.name)" type="danger" size="small">移除</el-button>
                </template>
              </el-table-column>
            </el-table>
          </el-tab-pane>
        </el-tabs>
    </el-dialog>
    <el-dialog :visible.sync="progressShow" :title=progress.title width="60%" :before-close="closeProgress">
      <div v-loading="progressLoading">
        <el-row v-for="(item,index) in progress.layer" style="margin-bottom: 10px; height: 24px;" >
          <el-tag style="float: left; width: 15%;height: 24px; line-height: 24px;" align="center">{{item.id}}</el-tag>
          <div style="float: left;width: 80%;margin-left: 10px;">
            <el-progress :percentage="item.progress" :text-inside="true" :stroke-width="24" status="success" v-if="item.progress === 100.0"></el-progress>
            <el-progress :percentage="item.progress" :text-inside="true" :stroke-width="24" v-else></el-progress>
          </div>
        </el-row>
      </div>
    </el-dialog>
    <el-dialog :visible.sync="deleteShow" title="删除" width="80%">
      <el-table
        :data="deleteContainerList" border stripe style="width: 100%">
        <el-table-column type="index" width="50"></el-table-column>
        <el-table-column prop="vul_name" width="150" :show-overflow-tooltip=true label="漏洞名称"></el-table-column>
        <el-table-column :show-overflow-tooltip=true prop="user_name" width="100" label="用户名"></el-table-column>
        <el-table-column prop="vul_host" width="200" :show-overflow-tooltip=true label="访问地址"></el-table-column>
        <el-table-column label="状态" width="85">
          <template slot-scope="{row}">
            <el-tag>{{row.container_status}}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="vul_desc" :show-overflow-tooltip=true width="300" label="漏洞描述"></el-table-column>
        <el-table-column prop="combination_desc" label="操作" :show-overflow-tooltip=true>
          <template slot-scope="{row}">
            <el-button size="mini" type="danger" icon="el-icon-delete" v-if="row.container_status === 'running' || row.container_status === 'stop'"
                       @click="delContainer(row)" >删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-dialog>
    <el-dialog :visible.sync="editShow" title="修改">
      <el-form label-width="80px" v-loading="editLoding" element-loading-text="修改中">
        <el-form-item label="漏洞名称">
          <el-input v-model="editVulInfo.image_vul_name" size="medium"></el-input>
        </el-form-item>
        <el-form-item label="镜像">
          <el-input v-model="editVulInfo.image_name" disabled></el-input>
        </el-form-item>
        <el-form-item label="Rank">
          <el-input-number v-model="editVulInfo.rank" :min="0.5" :max="5.0" :precision="1" :step="0.5" size="medium"></el-input-number>
          &nbsp;&nbsp;&nbsp;
          <el-tooltip content="默认分数为2.5分，可根据漏洞的利用难度进行评判" placement="top">
            <i class="el-icon-question"></i>
          </el-tooltip>
        </el-form-item>
        <el-form-item label="描述">
          <el-input type="textarea" v-model="editVulInfo.image_desc" size="medium"></el-input>
        </el-form-item>
        <el-form-item>
          <el-button type="primary"  @click="handleEditImage" size="medium">提 交</el-button>
        </el-form-item>
      </el-form>
    </el-dialog>
    <div class="filter-container">
      <el-input v-model="search" style="width: 230px;" size="medium"></el-input>
      <el-button class="filter-item" size="medium" style="margin-left: 10px;margin-bottom: 10px" type="primary" icon="el-icon-search" @click="handleQuery(1)">
        查询
      </el-button>
      <el-button class="filter-item" size="medium" style="margin-left: 10px;margin-bottom: 10px" type="primary" icon="el-icon-edit" @click="openCreate">
        添加
      </el-button>
    </div>
    <el-table :data="tableData" border stripe align = "center" style="width: 100%">
      <el-table-column type="index" width="50"> </el-table-column>
      <el-table-column prop="image_name" label="镜像名称" :show-overflow-tooltip=true ></el-table-column>
      <el-table-column prop="image_vul_name" label="漏洞名称" :show-overflow-tooltip=true></el-table-column>
      <el-table-column prop="image_port" label="端口" width="150"></el-table-column>
      <el-table-column prop="rank" label="分数" width="50"></el-table-column>
      <el-table-column prop="image_desc" :show-overflow-tooltip=true label="描述"> </el-table-column>
      <el-table-column fixed="right" label="操作" width="260">
        <template slot-scope="{row}">
          <el-tag style="display: inline-block;float: left;line-height: 28px;height: 28px; margin-left: 5px;"
                  @click="openProgress(row,1)" effect="dark" v-if="row.is_ok === false && row.status.task_id !== ''">
            <div style="display: inline-block;float: left"><span>下载中</span></div>
            <div style="display: inline-block;float: left">
              <el-progress style="margin-left: 3px;margin-top:3px;" type="circle" :stroke-width="3"
                           :show-text="false" :text-inside="false" :percentage="row.status.progress"
                           :width="20"></el-progress>
            </div>
          </el-tag>
          <el-button style="display: inline-block;float: left;margin-left: 5px;"
                     v-else-if="row.is_ok === false && row.status.task_id === ''"
                     size="mini"
                     type="primary"
                     icon="el-icon-download"
                     @click="downloadImg(row)">下载</el-button>
          <el-button style="display: inline-block;float: left;margin-left: 5px;"
                     v-if="(row.is_ok === true) || (row.is_ok === false && row.status.task_id === '')" size="mini"
                     icon="el-icon-edit"
                     type="primary"
                     @click="openEdit(row)">修改</el-button>
          <el-button style="display: inline-block;float: left;margin-left: 5px;"
            v-if="(row.is_ok === true) || (row.is_ok === false && row.status.task_id === '')" size="mini" type="danger"
            icon="el-icon-delete"
            @click="handleDelete(row)">删除</el-button>
          <el-tag style="display: inline-block;float: left;line-height: 28px;height: 28px; margin-left: 5px;"
                  type="success" effect="dark" v-if="row.is_ok === true && row.is_share === true">
            <div style="display: inline-block;float: left"><span>已分享</span></div>
          </el-tag>
          <el-button style="display: inline-block;float: left;margin-left: 5px;"
                     v-if="(row.is_ok === true && row.is_share === false && row.status.progress_status !== 'share')"
                     size="mini"
                     type="primary"
                     icon="el-icon-share"
                     @click="shareImg(row)">分享</el-button>
          <el-tag style="display: inline-block;float: left;line-height: 28px;height: 28px; margin-left: 5px;"
                  @click="openProgress(row,2)" effect="dark" v-if="row.is_ok === true && row.status.progress_status === 'share'">
            <div style="display: inline-block;float: left"><span>分享中</span></div>
            <div style="display: inline-block;float: left">
              <el-progress style="margin-left: 3px;margin-top:3px;" type="circle" :stroke-width="3"
                           :show-text="false" :text-inside="false" :percentage="row.status.progress"
                           :width="20"></el-progress>
            </div>
          </el-tag>
        </template>
      </el-table-column>
    </el-table>
    <div style="margin-top: 20px">
      <el-pagination :page-size="page.size" @current-change="handleQuery" layout="total, prev, pager, next, jumper"
        :total="page.total">
      </el-pagination>
    </div>
  </div>
</template>

<script>
  import { ImgList } from "@/api/docker"
  import { search } from "@/api/utils"
  import { ImageAdd, ImageDelete,ImageLocal,ImageLocalAdd,ImageShare,ImageDownload,ImageEdit } from "@/api/image"
  import { containerDel } from '@/api/container'
  import { getTask,batchTask,progressTask } from '@/api/tasks'

  export default {
    name: 'index',
    data() {
      return {
        tableData: [],
        search: "",
        localSearch: "",
        centerDialogVisible: false,
        startCon: false,
        vulInfo: {
          rank: "",
          name: "",
          vul_name: "",
          desc: "",
        },
        editShow: false,
        editLoding: false,
        editVulInfo:{
          rank: "",
          image_name: "",
          image_id: "",
          image_vul_name: "",
          image_desc: "",
        },
        imgType: "text",
        imgTypeText: "切换为文件",
        loading: false,
        summaries:[],
        taskCheckInterval :null,
        tmpImageNameList:[],
        localImageList:[],
        tmpLocalImageList:[],
        localLoading: true,
        selectLocalImages: [],
        progressShow: false,
        progressLoading: false,
        deleteShow: false,
        deleteContainerList: [],
        progress:{
          "title":"",
          "layer":[],
          "total":0,
          "count":0,
          "progress":0.0,
          "progressInterval": null,
        },
        taskList: [],
        taskDict: {},
        page:{
          total: 0,
          size: 20,
        }
      }
    },
    created() {
      this.initTableData()
      this.initSummariesList()
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
        ImgList(undefined, true, 1).then(response => {
          this.tableData = response.data.results
          this.page.total = response.data.count
          this.tableData.forEach((item, index, arr) => {
            let image_name = item.image_name
            if(this.tmpImageNameList.indexOf(image_name) > -1){
              this.$notify({
                title: '成功',
                message: image_name+" 添加成功",
                type: 'success'
              });
            }
          })
          let tmpTableData = response.data.results
          this.taskCheckInterval = window.setInterval(() => {
            setTimeout(()=>{
              this.checkTask(tmpTableData)
            },0)
          },2000)
        })
      },
      openCreate(){
        this.centerDialogVisible = true
        this.vulInfo.rank = 2.5
        this.vulInfo.name = ""
        this.vulInfo.vul_name = ""
        this.vulInfo.desc = ""
      },
      openProgress(row,flag){
        this.progress = {
          "title":"",
          "layer":[],
          "total":0,
          "count":0,
          "progress":0.0,
          "progressInterval": null,
        }
        this.progressShow = true
        this.progressLoading = true
        let taskId = row.status.task_id
        if(flag === 1){
          this.progress.title = "下载镜像："+row.image_name
        }else{
          this.progress.title = "分享镜像："+row.image_name
        }
        this.progress.progressInterval = window.setInterval(() => {
          setTimeout(()=>{
            this.progressLoading = false
            progressTask(taskId).then(response => {
              if(response.data.data != null  && response.data.status === 200){
                this.progress.count = response.data.data.progress_count
                this.progress.progress = response.data.data.progress
                this.progress.total = response.data.data.total
                this.progress.layer = response.data.data.layer
                if(this.progress.progress === 100.0 || (this.progress.count !== 0 && this.progress.total !== 0 && this.progress.count === this.progress.total)){
                  clearInterval(this.progress.progressInterval)
                  this.progressShow = false
                }
              }
            })
          },1.5)
        },2000)
      },
      openEdit(row){
        this.editShow = true
        this.editVulInfo = row
      },
      handleEditImage(){
        this.editLoding = true
        ImageEdit(this.editVulInfo.image_id,this.editVulInfo).then(response => {
          this.editLoding = false
          let rsp = response.data
          let msg = rsp.msg
          if(rsp.status === 200){
            this.$message({
              message: '修改成功!',
              type: 'success'
            });
            this.editShow = false
            this.initTableData()
          }else{
            this.$message({
              message: msg,
              type: 'error'
            });
          }
        })
      },
      closeProgress(){
        this.progressShow = false
        this.progressLoading = false
        try {
          clearInterval(this.progress.progressInterval)
        }catch (e) {

        }
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
      uploadImg() {
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
            if(msg.indexOf("成功") > -1 ){
              this.$notify({
                title: '成功',
                message: msg,
                type: 'success'
              });
              this.centerDialogVisible = false
              this.initTableData()
            }else{
              this.$notify({
                title: msg,
                message: msg,
                type: 'error'
              });
              this.centerDialogVisible = false
            }
          }else{
            this.$notify({
              title: '成功',
              message: data["msg"],
              type: 'success'
            });
            this.centerDialogVisible = false
            this.initTableData()
          }
        })
      },
      downloadImg(row){
        let imageId = row.image_id
        ImageDownload(imageId).then(response => {
          let rsp = response.data
          let msg = rsp["msg"]
          if(rsp.status === 200){
            if(msg != null && (msg.indexOf("成功") > -1 || msg.indexOf("失败") > -1 )){
              let tmpMsg = msg.replace("拉取镜像", "").replace("任务下发成功", "").replace(" ", "")
              this.tmpImageNameList.push(tmpMsg)
              if(msg.indexOf("成功") > -1 ){
                this.$notify({
                  title: '成功',
                  message: msg,
                  type: 'success'
                });
                this.initTableData()
              }else{
                this.$notify({
                  message: msg,
                  type: 'error'
                });
              }
            }else{
              this.$notify({
                message: msg,
                type: 'error'
              });
            }
          }else{
            this.$notify({
              message: msg,
              type: 'error'
            });
            this.centerDialogVisible = false
          }
        })
      },
      shareImg(row){
        row.status.status = 'share'
        ImageShare(row.image_id).then(response => {
          let rsp = response.data
          let status = rsp.status
          if(status === 200){
            // this.
          }else{
            this.$message({
              message:  rsp.msg,
              type: "error",
            })
          }
          this.initTableData()
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
                title: '成功',
                message: '删除成功!',
                type: 'success'
              });
              this.initTableData()
            }else{
              this.deleteShow = true
              this.deleteContainerList = data.data
              this.$message({
                title: '失败',
                message: data.msg,
                type: 'error'
              });
            }
          })
        }).catch(() => {
        });
      },
      handleQuery(val){
        ImgList(this.search, true, val).then(response => {
          this.tableData = response.data.results
          this.page.total = response.data.count
        })
      },
      handleSelect(item){
        this.vulInfo.name = item.value
        this.vulInfo.vul_name = item.value.replace("vulfocus/", "")
        this.vulInfo.desc = item.value.replace("vulfocus/", "")
      },
      checkTask(tableData){
        tableData.forEach((item, index, arr) => {
          let isOk = item["is_ok"]
          let taskId = item["status"]["task_id"]
          let status = item["status"]["progress_status"]
          if ((isOk === false && taskId != null && taskId !== "") || (isOk === true && taskId != null && taskId !== "" && status === "share")){
            if(this.taskList.indexOf(taskId) === -1){
              this.taskList.push(taskId)
              this.taskDict[taskId] = item
            }
          }
        })
        let taskIdStr = this.taskList.join(",")
        if(taskIdStr != null && taskIdStr !== ""){
          let formData = new FormData()
          formData.set("task_ids", taskIdStr)
          batchTask(formData).then(response => {
            let data = response.data.data
            for(let key in data){
              let taskMsg = data[key]
              let status = taskMsg["status"]
              if(status !== 1){
                this.removeArray(this.taskList, key)
                this.taskDict[key].is_ok = true
                if(taskMsg["data"]["status"] === 200){
                  let taskMsgData = taskMsg["data"]["data"]
                  try {
                    let imagePort = taskMsgData.replace("{\"image_port\":","").replace("}", "").replace(":", "").replace("\"", "").replace('"','')
                    this.taskDict[key].image_port = imagePort
                  }catch (e) {
                    //
                  }
                  try{
                    if(taskMsg["data"]["msg"].indexOf("分享") > -1){
                      this.taskDict[key].is_share = true
                      this.taskDict[key].status.progress_status = ""
                    }
                  }catch (e) {

                  }
                  this.$notify({
                    message: taskMsg["data"]["msg"],
                    type: 'success'
                  });
                }else{
                  try{
                    if(taskMsg["data"]["msg"].indexOf("分享") > -1){
                      this.taskDict[key].is_share = false
                      this.taskDict[key].status.progress_status = ""
                    }
                  }catch (e) {

                  }
                  this.$notify({
                    message: taskMsg["data"]["msg"],
                    type: 'error'
                  });
                }
              }else{
                this.taskDict[key].status.progress = taskMsg["progress"]
              }
            }
            if (this.taskList == null || this.taskList.length === 0){
              this.taskList = []
              this.taskDict = {}
              clearInterval(this.taskCheckInterval)
            }
          })
        }
        // return taskList
      },
      removeArray(taskList,val){
        for(let i = 0; i < taskList.length; i++) {
          if(taskList[i] === val) {
            taskList.splice(i, 1);
            break;
          }
        }
      },
      loadLocalImages(){
        this.localLoading = true
        ImageLocal().then(response => {
          let resp = response.data
          let status = resp.status
          let data = resp.data
          if(status === 200){
            this.localImageList = data
            this.tmpLocalImageList = data
          }
          this.localLoading = false
        })
      },
      handleClick(tab, event) {
        let name = tab.name
        if(name === "local"){
          this.loadLocalImages()
        }else{

        }
      },
      handleLocalRemove(name){
        for(let i = 0; i < this.localImageList.length; i++) {
          if(this.localImageList[i].name === name) {
            this.localImageList.splice(i, 1);
            break;
          }
        }
      },
      handleSelectLocalImages(val){
        let image_names = []
        for(let i in val){
          image_names.push(val[i].name)
        }
        this.selectLocalImages = image_names
      },
      batchLocalAdd(){
        if (this.selectLocalImages.length === 0){
          return
        }
        let data = new FormData()
        data.set("image_names", this.selectLocalImages.join(","))
        ImageLocalAdd(data).then(response => {
          let rsp = response.data
          let data = rsp.data
          let status = rsp.status
          if(status === 200){
            for(let i = 0; i < data.length; i ++){
              let msg = data[i]
              let tmpMsg = msg.replace(" ", "").replace("拉取镜像", "").replace("任务下发成功", "")
              this.tmpImageNameList.push(tmpMsg)

              this.$notify({
                title: '成功',
                message: msg,
                type: 'success'
              });
            }
            this.centerDialogVisible = false
            this.initTableData()
          }else if(status === 201){
            this.$notify({
              title: '失败',
              message: rsp["msg"],
              type: 'info'
            });
          }else{
            this.$notify({
              title: '失败',
              message: rsp["msg"],
              type: 'error'
            });
          }
        })
      },
      delContainer(row){
        containerDel(row.container_id).then(response => {
          let taskId = response.data["data"]
          let tmpDeleteContainerInterval = window.setInterval(() => {
            setTimeout(()=>{
              getTask(taskId).then(response=>{
                let responseStatus = response.data["status"]
                let responseData = response.data
                if (responseStatus === 1001){
                  // 一直轮训
                }else{
                  clearInterval(tmpDeleteContainerInterval)
                  if (responseStatus === 200) {
                    this.$message({
                      type: 'success',
                      message: '删除成功'
                    });
                    ImageDelete(row.image_id).then(response => {
                      let data = response.data
                      if(data.status !== 200){
                        this.deleteContainerList = data.data
                      }else{
                        this.$message({
                          type: 'success',
                          message: '删除成功'
                        });
                        this.deleteShow = false
                        this.initTableData()
                      }
                    })
                  }else{
                    this.$message({
                      message: responseData["msg"],
                      type: "error",
                    })
                  }
                }
              })
            },1)
          },1000)
        })
      }
    }
  }
</script>

<style scoped>

</style>
