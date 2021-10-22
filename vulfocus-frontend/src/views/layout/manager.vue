<template>
  <div class="app-container" >
    <div class="filter-container">
      <el-input v-model="search" class="sceneSearch" size="medium" placeholder="请输入关键字进行搜索" @keyup.enter.native="handleQuery">
        <i slot="prefix" class="el-input__icon el-icon-search"></i>
      </el-input>
    </div>
    <div style="margin-top: 10px;">
      <span>场景商店</span>
      <span v-if="senceStoreList.length>5" @click="showactive" style="color: #999999;float: right" >{{ showBtnSence?"查看更多":"收起" }}</span>
    </div>
    <div style="position: relative;overflow: hidden;">
      <el-drawer style="position:absolute;margin-top: 10px;color: #303133" title="场景商店"  :visible.sync="drawer" :direction="direction" size="100%">
        <el-row style="margin-top: 10px" :gutter="20">
          <el-col style="margin-top: 5px" v-for="(item,index1) in senceStoreList" :key="index1" :span="6">
            <el-card :body-style="{ padding: '2px'}" shadow="hover">
              <el-tooltip class="item" effect="dark" :content="item.layout_name" placement="top">
                <img fit="contain" @click="download_website_layout(item.layout_id)" :src="item.image_name" height="260px" width="100%">
              </el-tooltip>
            </el-card>
          </el-col>
        </el-row>
      </el-drawer>
      <div class="filter-container">
        <el-row style="margin-top: 10px">
          <el-col :class="activeSceneClass === index1 ? 'current':''"  :xs="12" :sm="12" :lg="{span: '4-8'}" v-for="(item,index1) in senceStoreList" v-if="index1 < sceneLength" :key="index1" style="width: 20%">
            <el-card :body-style="{ padding: '0px'}" shadow="hover">
              <el-tooltip class="item" effect="dark" :content="item.layout_name" placement="top">
                <img fit="contain" @click="download_website_layout(item.layout_id)" :src="item.image_name" height="180px" width="100%">
              </el-tooltip>
            </el-card>
          </el-col>
        </el-row>
      </div>
      <el-dialog :visible.sync="imageDialogVisible">
        <img width="100%" :src="dialogImageUrl" alt="">
      </el-dialog>
      <el-dialog :visible.sync="ymlDialogVisible">
        <el-input type="textarea" style="color:black;" autosize readonly v-model="dialogYml" ></el-input>
      </el-dialog>
      <el-tabs v-model="activeName" style="margin-top: 10px" @tab-click="currentTabs">
        <el-tab-pane label="全部" name="all">
          <div class="filter-container">
            <el-row :gutter="23">
              <el-col :span="4"  style="padding-bottom: 18px;">
                <el-card shadow="hover" :body-style="{ padding: '0px'}" style="height: 328px">
                  <el-row style="margin-top: 40%">
                    <el-col :span="8" :offset="8">
                      <i @click="addScene" class="el-icon-plus" style="font-size: 400%;position: relative;transform: translateX(20%)"></i>
                    </el-col>
                  </el-row>
                  <el-row>
                    <el-col :span="8" :offset="8">
                      <span class="word2" style="font-size:110%;position: relative;transform: translateX(20%)">添加场景</span>
                    </el-col>
                  </el-row>
                </el-card>
              </el-col>
              <el-col :span="4" v-for="(item,index) in sceneTableData" :key="index" style="padding-bottom: 18px;">
                <el-card :body-style="{ padding: '0px'}" shadow="hover" style="height: 328px">
                  <div style="position: relative">
                    <div class="main" style="position: absolute;" v-if="item.is_release === false">
                      <span class="word">未发布</span>
                    </div>
                    <img v-if="item.image_name !==imgpath" :src="item.image_name"  alt="" width="100%" height="250px"/>
                    <img v-else-if="item.image_name===imgpath" :src="modelimg"  alt="" width="100%" height="250px" />
                    <div v-if="item.is_release === false & item.type === 'layoutScene'" style="margin-top: -23px">
                      <el-row style="background-color:rgba(0,0,0,0.3)">
                        <el-col :xs="12" :sm="12" :lg="{span: '4-8'}" style="width: 20%">
                          <el-link type="info" @click="handleShowYml(item.id)" :underline="false" style="color: #ffffff" icon="el-icon-zoom-in">查看</el-link>
                        </el-col>
                        <el-col :xs="12" :sm="12" :lg="{span: '4-8'}" style="width: 20%">
                          <el-link type="info" @click="handleEdit(item.id)" :underline="false" style="color: #ffffff" icon="el-icon-edit">编辑</el-link>
                        </el-col>
                        <el-col :xs="12" :sm="12" :lg="{span: '4-8'}" style="width: 20%">
                          <el-link type="info" @click="handleDelete(item.id)" :underline="false" style="color: #ffffff" icon="el-icon-delete">删除</el-link>
                        </el-col>
                        <el-col :xs="12" :sm="12" :lg="{span: '4-8'}" style="width: 20%">
                          <el-link type="info" @click="handleDownload(item.id,item.name)" :underline="false" style="color: #ffffff" icon="el-icon-download">下载</el-link>
                        </el-col>
                        <el-col :xs="12" :sm="12" :lg="{span: '4-8'}" style="width: 20%">
                          <el-link v-if="item.status.task_id === ''" type="info" @click="handleRelease(item.id,item.is_uesful)" :underline="false" style="color: #ffffff" icon="el-icon-position">发布</el-link>
                          <el-link v-if="item.status.task_id !== ''" type="info" @click="openProgress(item,1)" :underline="false" style="color: #ffffff" icon="el-icon-loading">下载中</el-link>
                        </el-col>
                      </el-row>
                    </div>
                    <div v-else-if="item.is_release === true & item.type === 'layoutScene'" style="margin-top: -23px">
                      <el-row style="background-color:rgba(0,0,0,0.3)">
                        <el-col :span="6" style="position: relative">
                          <el-link type="info" @click="handleShowYml(item.id)" :underline="false" style="color: #ffffff" icon="el-icon-zoom-in">查看</el-link>
                        </el-col>
                        <el-col :span="6" style="position: relative">
                          <el-link type="info" @click="handleEdit(item.id)" :underline="false" style="color: #ffffff"  icon="el-icon-edit">编辑</el-link>
                        </el-col>
                        <el-col :span="6" style="position: relative">
                          <el-link type="info" @click="handleDelete(item.id)" :underline="false" style="color: #ffffff"  icon="el-icon-delete">删除</el-link>
                        </el-col>
                        <el-col :span="6" style="position: relative">
                          <el-link type="info" @click="handleDownload(item.id,item.name)" :underline="false" style="color: #ffffff" icon="el-icon-download">下载</el-link>
                        </el-col>
                      </el-row>
                    </div>
                    <div v-else-if="item.type !== 'layoutScene'" style="margin-top: -23px">
                      <el-row style="background-color:rgba(0,0,0,0.3)">
  <!--                      <el-col :span="6" :offset="6">-->
  <!--                        <el-link type="info" :underline="false" style="margin-top: -50px;" icon="el-icon-edit">编辑</el-link>-->
  <!--                      </el-col>-->
                        <el-col :span="12">
                          <el-link type="info" @click="delSceneTemp(item.id)" :underline="false" style="color: #ffffff" icon="el-icon-delete">删除</el-link>
                        </el-col>
                      </el-row>
                    </div>
                    <div class="container-title" style="margin-top: 0;">
                      <span style="color:#303133;margin-left: 5px;font-size: 14px;">{{item.name}}</span>
                    </div>
                    <div class="bottom clearfix" style="margin-top: 10px;height: 60px;">
                      <span style="color:#999;font-size: 14px;margin-left: 5px;" class="hoveDesc"> {{ item.desc }}</span>
                    </div>
                  </div>
                </el-card>
              </el-col>
            </el-row>
          </div>
        </el-tab-pane>
        <el-tab-pane label="环境编排" name="layout">
          <div class="filter-container">
            <el-row :gutter="23">
              <el-col :span="4" v-for="(item,index) in sceneTableData" :key="index" style="padding-bottom: 18px;">
                <el-card :body-style="{ padding: '0px'}" shadow="hover" style="height: 328px">
                  <div style="position: relative">
                    <div class="main" style=" position: absolute" v-if="item.is_release === false">
                      <span class="word">未发布</span>
                    </div>
                    <img v-if="item.image_name !==imgpath" :src="item.image_name"  alt="" width="100%" height="250px"/>
                    <img v-else-if="item.image_name===imgpath" :src="modelimg"  alt="" width="100%" height="250px" />
                    <div v-if="item.is_release === false & item.type === 'layoutScene'" style="margin-top: -23px">
                      <el-row style="background-color:rgba(0,0,0,0.3)">
                        <el-col :xs="12" :sm="12" :lg="{span: '4-8'}" style="width: 20%">
                          <el-link type="info" @click="handleShowYml(item.id)" :underline="false" style="color: #ffffff" icon="el-icon-zoom-in">查看</el-link>
                        </el-col>
                        <el-col :xs="12" :sm="12" :lg="{span: '4-8'}" style="width: 20%">
                          <el-link type="info" @click="handleEdit(item.id)" :underline="false" style="color: #ffffff" icon="el-icon-edit">编辑</el-link>
                        </el-col>
                        <el-col :xs="12" :sm="12" :lg="{span: '4-8'}" style="width: 20%">
                          <el-link type="info" @click="handleDelete(item.id)" :underline="false" style="color: #ffffff" icon="el-icon-delete">删除</el-link>
                        </el-col>
                        <el-col :xs="12" :sm="12" :lg="{span: '4-8'}" style="width: 20%">
                          <el-link type="info" @click="handleDownload(item.id,item.name)" :underline="false" style="color: #ffffff" icon="el-icon-download">下载</el-link>
                        </el-col>
                        <el-col :xs="12" :sm="12" :lg="{span: '4-8'}" style="width: 20%">
                          <el-link v-if="item.status.task_id === ''" type="info" @click="handleRelease(item.id,item.is_uesful)" :underline="false" style="color: #ffffff" icon="el-icon-position">发布</el-link>
                          <el-link v-if="item.status.task_id !== ''" type="info" @click="openProgress(item,1)" :underline="false" style="color: #ffffff" icon="el-icon-loading">下载中</el-link>
                        </el-col>
                      </el-row>
                    </div>
                    <div v-else-if="item.is_release === true & item.type === 'layoutScene'" style="margin-top: -23px;">
                      <el-row style="background-color:rgba(0,0,0,0.3)">
                        <el-col :span="6" style="position: relative">
                          <el-link type="info" @click="handleShowYml(item.id)" :underline="false" style="color: #ffffff" icon="el-icon-zoom-in">查看</el-link>
                        </el-col>
                        <el-col :span="6" style="position: relative">
                          <el-link type="info" @click="handleEdit(item.id)" :underline="false" style="color: #ffffff" icon="el-icon-edit">编辑</el-link>
                        </el-col>
                        <el-col :span="6" style="position: relative">
                          <el-link type="info" @click="handleDelete(item.id)" :underline="false" style="color: #ffffff" icon="el-icon-delete">删除</el-link>
                        </el-col>
                        <el-col :span="6" style="position: relative">
                          <el-link type="info" @click="handleDownload(item.id,item.name)" :underline="false" style="color: #ffffff" icon="el-icon-download">下载</el-link>
                        </el-col>
                      </el-row>
                    </div>
                    <div class="container-title" style="margin-top: 0;">
                      <span style="color:#303133;margin-left: 5px;font-size: 14px;">{{item.name}}</span>
                    </div>
                    <div class="bottom clearfix" style="margin-top: 10px;height: 60px;">
                      <span style="color:#999;font-size: 14px;margin-left: 5px;" class="hoveDesc"> {{ item.desc }}</span>
                    </div>
                  </div>
                </el-card>
              </el-col>
            </el-row>
          </div>
        </el-tab-pane>
        <el-tab-pane label="计时场景" name="time">
          <div class="filter-container">
            <el-row :gutter="23">
              <el-col :span="4" v-for="(item,index) in sceneTableData" :key="index" style="padding-bottom: 18px;">
                <el-card :body-style="{ padding: '0px'}" shadow="hover" style="height: 328px">
                  <div style="position: relative">
                    <img v-if="item.image_name !==imgpath" :src="item.image_name"  alt="" width="100%" height="250px"/>
                    <img v-else-if="item.image_name===imgpath" :src="modelimg"  alt="" width="100%" height="250px" />
                    <div v-if="item.type !== 'layoutScene'" style="margin-top: -23px;">
                      <el-row style="background-color:rgba(0,0,0,0.3)">
  <!--                      <el-col :span="6" :offset="6">-->
  <!--                        <el-link type="info" :underline="false" style="margin-top: -50px;" icon="el-icon-edit">编辑</el-link>-->
  <!--                      </el-col>-->
                        <el-col :span="12">
                          <el-link type="info" @click="delSceneTemp(item.id)" :underline="false" style="color: #ffffff" icon="el-icon-delete">删除</el-link>
                        </el-col>
                      </el-row>
                    </div>
                    <div class="container-title" style="margin-top: 0;">
                      <span style="color:#303133;margin-left: 5px;font-size: 14px;">{{item.name}}</span>
                    </div>
                    <div class="bottom clearfix" style="margin-top: 10px;height: 60px;">
                      <span style="color:#999;font-size: 14px;margin-left: 5px;" class="hoveDesc"> {{ item.desc }}</span>
                    </div>
                  </div>
                </el-card>
              </el-col>
            </el-row>
          </div>
        </el-tab-pane>
      </el-tabs>
      <el-dialog title="选择创建类型" :visible.sync="selectSceneDialog" width="20%" center>
        <el-row>
          <el-col :span="8" :offset="8" style="position: relative;transform: translateX(-5%)">
            <el-button @click="handleOpenCreate" type="primary" plain>创建编排模式</el-button>
          </el-col>
        </el-row>
        <el-row style="margin-top: 10%">
          <el-col :span="8" :offset="8" style="position: relative;transform: translateX(-5%)">
            <el-button @click="handleCreateTemp" type="primary" plain>创建计时模式</el-button>
          </el-col>
        </el-row>
      </el-dialog>
      <el-dialog :visible.sync="createSceneTempDialog" title="创建计时盲盒" width="80%" height="100%">
        <v-createtemp></v-createtemp>
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
      <div style="margin-top: 20px">
        <el-pagination
          :page-size="page.size"
          @current-change="layoutListData"
          layout="total, prev, pager, next, jumper"
          :total="page.total">
        </el-pagination>
      </div>
    </div>
  </div>
</template>

<script>
import {layoutList, layoutRelease, layoutDelete,layoutDownload,download_layout_image,getOfficialWebsiteLayout,downloadWebsiteLayout } from '@/api/layout'
import { getSceneData } from '@/api/scene'
import { timetempdelete } from '@/api/timemoudel'
import {layoutbathchTask} from '@/api/tasks'
import timetemp from "../manager/timetemp";
import { progressTask } from '@/api/tasks'
export default {
  name: 'manager',
  inject: ['reload'],
  data(){
    return {
      tableData: [],
      search: "",
      page:{
        total: 0,
        size: 20,
      },
      isRelease: false,
      imageDialogVisible: false,
      dialogImageUrl: "",
      ymlDialogVisible: false,
      dialogYml: "",
      activeName:'all',
      imgpath: '/images/',
      modelimg: require("../../assets/modelbg.jpg"),
      sceneTableData:[],
      selectSceneDialog:false,
      createSceneTempDialog:false,
      showBtnSence:true,
      senceStoreList:[],
      newLayoutFile: new FormData(),
      taskCheckInterval :null,
      taskList: [],
      taskDict: {},
      progress:{
        "title":"",
        "layer":[],
        "total":0,
        "count":0,
        "progress":0.0,
        "progressInterval": null,
      },
      progressShow: false,
      progressLoading: false,
      activeSceneClass:0,
      sceneLength:5,
      drawer:false,
      direction:'ttb'

    }
  },
  components:{
    'v-createtemp':timetemp
  },
  created() {
    // this.layoutListData(1)
    this.getScene()
    this.get_official_website()
  },
  methods:{
    layoutListData(page){
      this.tableData = []
      layoutList(this.search, page).then(response => {
        let rsp = response.data
        rsp.results.forEach((info,index) => {
          info.image_name = '/images/'+ info.image_name
          this.tableData.push(info)
        })
        this.page.total = rsp.count
      }).catch(err => {
        this.$message({
          type: 'error',
          message: '服务器内部错误!'
        })
      })
    },
    handleQuery(){
      // this.tableData = []
      // this.layoutListData(1)
      this.getScene(1)
    },
    handleOpenCreate(){
      this.$router.push({path:'/layout/index'})
    },
    handleDelete(id){
      this.$confirm('确认删除？删除会影响用户得分', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(()=>{
        let ids = String(id)
        layoutDelete(ids).then(response => {
          let rsp = response.data
          if(rsp.status === 200){
            this.$message({
              message: "删除成功",
              type: 'success'
            })
            this.getScene(1)
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
      }).catch()
    },
    handleShowImage(row){
      this.dialogImageUrl = row.image_name
      this.imageDialogVisible = true
    },
    handleShowYml(id){
      if (id){
        let ids = String(id)
        layoutList(ids).then(response=>{
          let rsp = response.data
          let yml_content = ''
          rsp.results.forEach((info,index) => {
            yml_content = info.yml_content
          })
          this.dialogYml = yml_content
          this.ymlDialogVisible = true
        })
      }else {
        this.$message({
          type: 'error',
          message: '不存在的场景!'
        })
      }
    },
    handleEdit(id){
      if (id){
        let ids = String(id)
        layoutList(ids).then(response=>{
          let rsp = response.data
          let rows = {}
          rsp.results.forEach((info,index) => {
            rows = info
          })
          this.$router.push({path:'/layout/index', query: {layoutId: ids, layoutData: rows}})
        })
      }else {
        this.$message({
          type: 'error',
          message: '不存在的场景!'
        })
      }
    },
    handleRelease(id,is_uesful){
      let ids = String(id)
      if (is_uesful === false){
      this.$confirm('相关镜像未下载，下载后可发布，是否下载?', '提示', {
        center: true,
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        this.downloadImage(ids)
      }).catch(() => {
        this.$message({
          type: 'info',
          message: '已取消下载'
        });
      });
      }else {
      layoutRelease(ids).then(response=>{
        let rsp = response.data
        let status = rsp.status
        if (status === 200){
          this.$message({
            message: "发布成功",
            type: 'success'
          })
          this.getScene(1)
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
    }
    },
    handleCreateTemp(){
      this.createSceneTempDialog = true
    },
    delSceneTemp(id){
      let ids = String(id)
      timetempdelete(ids).then(response => {
        let data = response.data
        if (data.code === 200){
          this.$message({
            type:'success',
            message: data.message
          })
          this.getScene(1)
        }else{
          this.$message({
            type:'error',
            message: data.message
          })
        }
      })
    },
    currentTabs(tab, event){
      this.activeName = tab.name
      this.getScene(1,this.activeName)
    },
    getScene(page){
      getSceneData(this.search,page,this.activeName,'backstage').then(response=>{
        this.sceneTableData = []
        if (response.data.code === 200){
          response.data.result.forEach((info,index) => {
            info.image_name = '/images/'+ info.image_name
            this.sceneTableData.push(info)
          })
          this.page.total = response.data.count
        }else {
          this.$message({
            type: 'error',
            message: '数据返回失败!'
          })
        }
      })
    },
    addScene(){
      this.selectSceneDialog = true
    },
    handleDownload(id,name){
      let ids = String(id)
      layoutDownload(ids).then(response => {
        const url = window.URL.createObjectURL(new Blob([response.data], { type: 'application/zip' }))
        const link = window.document.createElement('a')
        link.style.display = 'none'
        link.href = url
        link.setAttribute('download', name+'.zip')
        document.body.appendChild(link)
        link.click()
      })
    },
    checkTask(tableData){
      tableData.forEach((item,index, arr) => {
        let isUserful = item["is_uesful"]
        let taskId = item["status"]["task_id"]
        if(isUserful === false && taskId !=null && taskId !== ""){
          if(this.taskList.indexOf(taskId) === -1){
            this.taskList.push(taskId)
            this.taskDict[taskId] = item
          }
        }
      })
      let taskIdStr = this.taskList.join(",")
      if(taskIdStr !=null && taskIdStr !==""){
        let formData = new FormData()
        formData.set("task_ids", taskIdStr)
        layoutbathchTask(formData).then(response => {
          let data = response.data.data
          for(let key in data){
            let taskMsg = data[key]
            let status = taskMsg["status"]
            if(status!==1){
              this.removeArray(this.taskList, key)
              this.taskDict[key].is_uesful = true
              this.$notify({
                    message: '场景下载成功',
                    type: 'success'
                  })
            }
            else{
              this.taskDict[key].status.progress = taskMsg["progress"]
            }
          }
          if(this.taskLists.length === 0 || this.taskLists === null){
            this.taskLists = []
            this.taskDict = {}
            clearInterval(this.taskCheckInterval)
          }
        })
      }
    },
    removeArray(taskList,val){
      for(let i = 0; i < taskList.length; i++) {
        if(taskList[i] === val) {
          taskList.splice(i, 1);
          break;
        }
      }
    },
    downloadImage(ids){
      let formdata = new FormData()
      formdata.set("layout_image_id",ids)
      download_layout_image(formdata).then(response => {
        let data = response.data
        if(data.code === 200){
          this.$message({
            message:data.msg,
            type:'success'
          })
          this.reload()
        }
        else{
          this.$message({
            message:data.msg,
            type:'error'
          })
        }
      })
      this.getScene(1)
    },
    openProgress(item,flag){
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
        let taskId = item.status.task_id
        if(flag === 1){
          this.progress.title = "下载相关镜像："+item.name
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
    closeProgress(){
      this.progressShow = false
      this.progressLoading = false
      try {
        clearInterval(this.progress.progressInterval)
      }catch (e) {

      }
    },
    get_official_website(){
      getOfficialWebsiteLayout().then(response=>{
        this.senceStoreList = response.data.data
      })
    },
    download_website_layout(id){
      let layoutdata = new FormData()
      if (id){
        let ids = String(id)
        layoutdata.set("layout_id",ids)
        this.$confirm('是否下载官网场景信息?', '提示', {
        center: true,
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
        }).then(() => {
          downloadWebsiteLayout(layoutdata).then(response=>{
            if (response.data.code===200){
              this.$message({
                type: 'success',
                message: response.data.msg
              });
              this.reload()
            }else {
              this.$message({
                type: 'error',
                message: response.data.msg
              });
            }
          })
        }).catch(() => {
          this.$message({
            type: 'info',
            message: '已取消下载'
          });
        });
      }else {
        this.$message({
          type: 'error',
          message: '错误的场景id'
        });
      }
    },
    showactive(){
      this.drawer = true
    }
  }
}
</script>

<style scoped>

.word {
  z-index: 53;
  position: absolute;
  top: 6px;
  width: 28px;
  display: block;
  overflow-wrap: break-word;
  margin-left: 20px;
  color: rgba(255, 255, 255, 1);
  font-size: 14px;
  white-space: nowrap;
  line-height: 14px;
}

.main {
  z-index: 52;
  width: 70px;
  height: 24px;
  margin-top: 20px;
  border-radius: 12px 0 0 12px;
  background-color: rgba(250, 63, 63, 1);
}

.hoveDesc {
  text-align: left;
  overflow: hidden;
  text-overflow: ellipsis;
  -o-text-overflow: ellipsis;
  white-space: nowrap;
  width:auto;
  display:block;
  word-break:keep-all;
  margin-top: 2px;
}

.word2 {
  z-index: 33;
  width: 56px;
  display: block;
  overflow-wrap: break-word;
  color: rgba(96, 98, 102, 1);
  font-size: 14px;
  font-family: MicrosoftYaHei;
  white-space: nowrap;
  line-height: 14px;
  margin-top: 32px;
}

.sceneSearch{
  width: 360px;
  height: 32px;
  background: #F2F4F7;
  border-radius: 4px;
}

</style>
