<template>
  <div class="dashboard-container">
    <el-dialog :visible.sync="centerDialogVisible" @close="handleDialogClose"  title="镜像信息">
      <i  class="el-icon-reading"  v-if="this.countlist.length===0"  v-model="drawer" @click="openDrawer" style="position:absolute;z-index: 9999;color: rgb(140, 197, 255);left:100px;top: 21px;font-size: 20px"></i>
      <div class="text item" v-loading="startCon" element-loading-text="环境启动中" >
        <div class="text item">
          访问地址: {{vul_host}}
        </div>
        <div class="text item">
          映射端口：
          <el-tag v-for="(value, key) in vul_port" :key="key" style="margin-right: 5px;">
            {{key}}:{{value}}
          </el-tag>
        </div>
        <div class="text item">
          名称: {{images_name}}
        </div>
        <div class="text item">
          描述: {{images_desc}}
        </div>
        <el-form v-if="is_flag===true">
          <el-form-item label="Flag" >
            <el-input v-model="input" placeholder="请输入Flag：格式flag-{xxxxxxxx}" ></el-input>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="subFlag(container_id,input.trim())" :disabled="cStatus">提 交</el-button>
          </el-form-item>
        </el-form>
         <div>
          <el-drawer :title="images_name+' writeup'"  :visible="drawer" size="50%" :direction="derection" modal="false" append-to-body="true" :before-close="closeDrawer" >
              <div>
                <el-row>
                  <el-col :span="1"></el-col>
                  <el-col :span="22">
                    <div class="container" v-if="drawerFlag===false && writeup_date !== ''">
                      <ViewerEditor v-model="writeup_date" ref="myset" height="600px" ></ViewerEditor>
                    </div>
                    <div class="container" v-else-if="drawerFlag===false && writeup_date === ''">
                      <ViewerEditor v-model="writeup_date" ref="myset" height="600px" ></ViewerEditor>
                      <el-empty description="当前环境还没有writeup，赶紧去官网发表解题思路吧">
                      </el-empty>
                    </div>
                  </el-col>
                </el-row>
              </div>
          </el-drawer>
        </div>
      </div>
    </el-dialog>
    <el-card class="box-card" v-if="this.countlist.length===0">
      <div style="margin-left: 10px">
          <el-input v-model="search" style="width: 230px;margin-left: 6px" size="medium" @keyup.enter.native="handleQuery(1)" ></el-input>
          <el-button class="filter-item" size="medium" style="margin-left: 10px;margin-bottom: 10px" type="primary" icon="el-icon-search" @click="handleQuery(1)">
            查询
          </el-button>
          <el-button  id="first-bmh" type="primary" style="left: 10px;display:none" size="medium" ref="showTips" @click="showTips" >新手引导</el-button>
        </div>
      <div class="filter-line">
        <div class="filter-name" style="width: 150px">
          难易程度
        </div>
        <div class="filter-content">
          <span :class="activeClass1 === index ? 'current':''" @click="selectDiff(index,item)" v-for="(item,index) in DifficultyList" >{{item.lable}}</span>
        </div>
      </div>
      <div class="filter-line">
        <div class="filter-name">
          开发语言
        </div>
        <div class="filter-content">
          <span :class="activeClass2 === index ? 'current':''" @click="selectLan(index,item)" v-for="(item,index) in languageList" v-if="index <= taglength2" >{{item.value}}</span>
          <span v-if="languageList.length>10" style="color: #36a3f7" @click="showactive('taglength2')" >{{ showBtnTag2?"更多...":"收起" }}</span>
        </div>
      </div>
      <div class="filter-line">
        <div class="filter-name" >
          漏洞类型
        </div>
        <div class="filter-content">
          <span :class="activeClass3 === index ? 'current':''" @click="selectDeg(index,item)" v-for="(item,index) in degreeList" v-if="index <= taglength3" >{{item.value}}</span>
          <span v-if="degreeList.length>10" style="color: #36a3f7" @click="showactive('taglength3')" >{{ showBtnTag3?"更多...":"收起" }}</span>
        </div>
      </div>
      <div class="filter-line">
        <div class="filter-name">
          数据库
        </div>
        <div class="filter-content">
          <span :class="activeClass5 === index ? 'current':''" @click="selectSql(index,item)" v-for="(item,index) in databaseList" v-if="index <= taglength5" >{{item.value}}</span>
          <span v-if="databaseList.length>10" style="color: #36a3f7" @click="showactive('taglength5')" >{{ showBtnTag5?"更多...":"收起" }}</span>
        </div>
      </div>
      <div class="filter-line">
        <div class="filter-name">
          框架
        </div>
        <div class="filter-content">
          <span :class="activeClass4 === index ? 'current':''" @click="selectIfy(index,item)" v-for="(item,index) in classifyList" v-if="index <= taglength4">{{item.value}}</span>
          <span v-if="classifyList.length>10" style="color: #36a3f7" @click="showactive('taglength4')" >{{ showBtnTag4?"更多...":"收起" }}</span>
        </div>
      </div>
    </el-card>
    <el-divider style="margin-top: 1px"></el-divider>
    <el-tabs v-model="activeName" style="margin-top: 10px" @tab-click="currentTabs">
      <el-tab-pane label="全部" name="all">
        <el-row :gutter="24" id="first-bmh3" v-loading="loading">
          <el-col :span="6" v-for="(item,index) in listdata" :key="index" style="padding-bottom: 18px;">
            <el-card :body-style="{ padding: '8px' }" shadow="hover"
                     @click.native=" item.status.status === 'running' && open(item.image_id,item.image_vul_name,item.image_desc,item.status.status,item.status.container_id,item)" >
              <div class="clearfix"  style="position: relative" >
                <div style=" position:absolute;right:0;top:0"><img v-if="item.status.is_check === true" style="width: 60%;height: 60%; float: right" src="../../assets/Customs.png" /></div>
                <div style="display: inline-block;height: 20px;line-height: 20px;min-height: 20px;max-height: 20px;">
                  <svg-icon icon-class="bug"  style="font-size: 20px;"/>
                  <el-tooltip v-if="(item.status.status === 'stop' || item.status.status === 'delete') && item.status.is_check === true" content="已通过" placement="top">
                  </el-tooltip>
                  <el-tooltip v-else-if="item.status.status === 'running'" content="运行中" placement="top">
                    <i style="color: #20a0ff;" class="el-icon-loading"></i>
                  </el-tooltip>
                  <el-tooltip v-else-if="item.status.status === 'stop' && item.status.is_check === false" content="暂停中" placement="top">
                    <svg-icon style="color: #20a0ff;" icon-class="stop" />
                  </el-tooltip>
                  <div style="display: inline-block;margin: 0;" v-if="item.status.status === 'running' && item.status.start_date !== null && item.status.start_date !=='' && item.status.end_date !== null && item.status.end_date !== '' && item.status.end_date !== 0">
                    <el-tooltip content="容器剩余时间，0 为用不过期" placement="top">
                      <i class="el-icon-time"></i>
                    </el-tooltip>
                    <count-down style="display: inline-block;height: 20px;line-height: 20px;size: 20px;margin-block-start: 0em;margin-block-end: 0em;" v-on:end_callback="stop(item.status.container_id, item,expire)" :currentTime="item.status.now" :startTime=item.status.now :endTime=item.status.end_date :secondsTxt="''"></count-down>
                  </div>
                  <div style="display: inline-block;" v-else-if="item.status.status === 'running' && item.status.start_date !== null && item.status.start_date !=='' && item.status.end_date !== null && item.status.end_date !== '' && item.status.end_date === 0">
                    <el-tooltip content="容器剩余时间，0 为用不过期" placement="top">
                      <i class="el-icon-time"></i>
                    </el-tooltip>
                    <p style="display: inline-block;">-1</p>
                  </div>
                  <div v-else style="display: inline-block;">
                    <p style="display: inline-block;margin-block-start: 1em;margin-block-end: 1em"></p>
                  </div>
                </div>
                <div style="margin-top: 7px;">
                  <el-rate v-model=item.rank disabled show-score text-color="#ff9900" score-template={value}></el-rate>
                </div>
              </div>
              <div style="padding: 5px;" >
                <div class="container-title">
                <span>{{item.image_vul_name}}</span>
                </div>
                <div class="bottom clearfix">
                  <div class="time container-title">{{ item.image_desc }}</div>
                </div>
                <el-row>
                  <el-button type="primary" @click.stop="stop(item.status.container_id,item)" :disabled="item.status.stop_flag" size="mini" v-if="item.status.status === 'running'">停止</el-button>
                  <el-button type="primary" @click.stop="open(item.image_id,item.image_vul_name,item.image_desc,item.status.status,item.status.container_id,item)" :disabled="item.status.start_flag" size="mini" v-else="item.status.status === '' || item.status.status === 'stop'">启动</el-button>
                  <el-button type="primary" @click.stop="deleteContainer(item.status.container_id,item)" v-if="item.status.status === 'running' || item.status.status === 'stop'" :disabled="item.status.delete_flag" size="mini" icon="el-icon-stopwatch">删除</el-button>
                </el-row>
              </div>
            </el-card>
          </el-col>
        </el-row>
        <div style="margin-top: 20px">
          <el-pagination
            :page-size="page.size"
            @current-change="handleQuery"
            layout="total, prev, pager, next, jumper"
            :total="page.total1">
          </el-pagination>
        </div>
      </el-tab-pane>
      <el-tab-pane label="已启动" name="started">
        <el-row :gutter="24" v-loading="loading">
          <el-col :span="6" v-for="(item,index) in startedlistdata" :key="index" style="padding-bottom: 18px;">
            <el-card :body-style="{ padding: '8px' }" shadow="hover"
                     @click.native=" item.status.status === 'running' && open(item.image_id,item.image_vul_name,item.image_desc,item.status.status,item.status.container_id,item)" >
              <div class="clearfix"  style="position: relative" >
                <div style=" position:absolute;right:0;top:0"><img v-if="item.status.is_check === true" style="width: 60%;height: 60%; float: right" src="../../assets/Customs.png" /></div>
                <div style="display: inline-block;height: 20px;line-height: 20px;min-height: 20px;max-height: 20px;">
                  <svg-icon icon-class="bug"  style="font-size: 20px;"/>
                  <el-tooltip v-if="(item.status.status === 'stop' || item.status.status === 'delete') && item.status.is_check === true" content="已通过" placement="top">
                  </el-tooltip>
                  <el-tooltip v-else-if="item.status.status === 'running'" content="运行中" placement="top">
                    <i style="color: #20a0ff;" class="el-icon-loading"></i>
                  </el-tooltip>
                  <el-tooltip v-else-if="item.status.status === 'stop' && item.status.is_check === false" content="暂停中" placement="top">
                    <svg-icon style="color: #20a0ff;" icon-class="stop" />
                  </el-tooltip>
                  <div style="display: inline-block;margin: 0;" v-if="item.status.status === 'running' && item.status.start_date !== null && item.status.start_date !=='' && item.status.end_date !== null && item.status.end_date !== '' && item.status.end_date !== 0">
                    <el-tooltip content="容器剩余时间，0 为用不过期" placement="top">
                      <i class="el-icon-time"></i>
                    </el-tooltip>
                    <count-down style="display: inline-block;height: 20px;line-height: 20px;size: 20px;margin-block-start: 0em;margin-block-end: 0em;" v-on:end_callback="stop(item.status.container_id, item,expire)" :currentTime="item.status.now" :startTime=item.status.now :endTime=item.status.end_date :secondsTxt="''"></count-down>
                  </div>
                  <div style="display: inline-block;" v-else-if="item.status.status === 'running' && item.status.start_date !== null && item.status.start_date !=='' && item.status.end_date !== null && item.status.end_date !== '' && item.status.end_date === 0">
                    <el-tooltip content="容器剩余时间，0 为用不过期" placement="top">
                      <i class="el-icon-time"></i>
                    </el-tooltip>
                    <p style="display: inline-block;">-1</p>
                  </div>
                  <div v-else style="display: inline-block;">
                    <p style="display: inline-block;margin-block-start: 1em;margin-block-end: 1em"></p>
                  </div>
                </div>
                <div style="margin-top: 7px;">
                  <el-rate v-model=item.rank disabled show-score text-color="#ff9900" score-template={value}></el-rate>
                </div>
              </div>
              <div style="padding: 5px;" >
                <div class="container-title">
                <span>{{item.image_vul_name}}</span>
                </div>
                <div class="bottom clearfix">
                  <div class="time container-title">{{ item.image_desc }}</div>
                </div>
                <el-row>
                  <el-button type="primary" @click.stop="stop(item.status.container_id,item)" :disabled="item.status.stop_flag" size="mini" v-if="item.status.status === 'running'">停止</el-button>
                  <el-button type="primary" @click.stop="open(item.image_id,item.image_vul_name,item.image_desc,item.status.status,item.status.container_id,item)" :disabled="item.status.start_flag" size="mini" v-else="item.status.status === '' || item.status.status === 'stop'">启动</el-button>
                  <el-button type="primary" @click.stop="deleteContainer(item.status.container_id,item)" v-if="item.status.status === 'running' || item.status.status === 'stop'" :disabled="item.status.delete_flag" size="mini" icon="el-icon-stopwatch">删除</el-button>
                </el-row>
              </div>
            </el-card>
          </el-col>
        </el-row>
        <div style="margin-top: 20px">
          <el-pagination
            :page-size="page.size"
            @current-change="handleQuery"
            layout="total, prev, pager, next, jumper"
            :total="page.total2">
          </el-pagination>
        </div>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script>
import { ImgList,SubFlag,ContainerSTART,ContainerDelete,ContainerStop,ImgDashboard,getWriteup,get_container_status } from '@/api/docker'
import { publicMethod,gettimetemp } from '@/api/timemoudel'
import { getTask } from '@/api/tasks'
import CountDown from 'vue2-countdown'
import { Notification } from 'element-ui'
import {stoptimetemp} from "@/api/timemoudel";
import Driver from "driver.js"
import "driver.js/dist/driver.min.css"
import MarkdownEditor from '@/components/MarkdownEditor'
import ViewerEditor from '@/components/ViewerEditor'
import 'codemirror/lib/codemirror.css' // codemirror
import 'tui-editor/dist/tui-editor.css' // editor ui
import 'tui-editor/dist/tui-editor-contents.css' // editor content
import { mapGetters } from 'vuex'
import codeSyntaxHighlight from "@toast-ui/editor-plugin-code-syntax-highlight";
import hljs from "highlight.js";
import Editor from 'tui-editor'
import { Loading } from "element-ui"

export default {
  inject: ['reload'],
  name: 'Dashboard',
  components: {
    CountDown,
    MarkdownEditor,
    ViewerEditor,
  },
  replace:true,
  data() {
    return {
      page:{
        total1: 0,
        total2: 0,
        size: 20,
      },
      activeClass1: 0,
      activeClass2: 0,
      activeClass3: 0,
      activeClass4: 0,
      activeClass5: 0,
      taglength2: 10,
      taglength3: 10,
      taglength4: 10,
      taglength5: 10,
      showBtnTag2: true,
      showBtnTag3: true,
      showBtnTag4: true,
      showBtnTag5: true,
      DifficultyList:[
        {value:0, lable:"全部"},
        {value:0.5, lable:"入门"},
        {value:2.0, lable:"初级"},
        {value:3.5, lable:"中级"},
        {value:5, lable:"高级"},
      ],
      drawerFlag:false,
      drawer:false,
      derection:"btt",
      listdata: [],
      startedlistdata: [],
      vul_host: "",
      radioStatus:false,
      centerDialogVisible: false,
      startCon:false,
      startTime:(new Date()).getTime(),
      input: "",
      images_id: "",
      container_id: "",
      images_name: "",
      writeup_date_name:"",
      images_desc: "",
      writeup_date:"",
      is_flag:true,
      expire:true,
      is_docker_compose:false,
      item_raw_data: "",
      cStatus: true,
      search: "",
      searchForm:{
        time_img_type:"",
        rank_range:0
      },
      user:{
        greenhand:false
      },
      vul_port:{},
      countlist:[],
      notifications: {},
      degreeList:[
        {value:"全部"},
      ],
      languageList:[
        {value:"全部"},
      ],
      databaseList:[
        {value:"全部"},
      ],
      classifyList:[
        {value:"全部"},
      ],
      allTag:[],
      allTag2:[],
      allTag3:[],
      allTag4:[],
      allTag5:[],
      searchRank:0,
      loading:true,
      firstLogin:false,
      current_page:1,
      open_flag:false,
      activeName:'all',
      };
    },
  created() {
    this.listData(1)
    this.timeData()
    this.getUser()
  },
  beforeDestroy(){
    Notification.closeAll()
  },
  computed: {
    ...mapGetters([
      'name',
      'avatar',
      'roles',
      'rank',
      'email',
      'greenhand',
    ])
  },
  methods:{
      timeData(){
        gettimetemp().then(response => {
          this.countlist = response.data.results
          if (this.countlist.length===0){
          }else {
            this.countlist[0].end_date = publicMethod.getTimestamp(this.countlist[0].end_date)
            this.countlist[0].start_date = publicMethod.getTimestamp(this.get_time)
            this.$notify({
              title: '计时模式',
              message:<count-down currentTime={this.countlist[0].start_date} startTime={this.countlist[0].start_date} endTime={this.countlist[0].end_date} dayTxt={"天"} hourTxt={"小时"} minutesTxt={"分钟"} secondsTxt={"秒"}></count-down>,
              duration: 0,
              position: 'bottom-right',
              showClose: false,
              dangerouslyUseHTMLString:true,
            });
          }})
      },
      changetableinit(){
      // 当用户在切换tab页时进行数据的初始化
        this.current_page = 1;
        this.loading = true;
        this.listdata = [];
        this.startedlistdata = [];
        this.page.total = 0;
      },
      listData() {
          ImgDashboard().then(response => {
            this.listdata = response.data.results
            this.page.total1 = response.data.count
            this.degreeList = [{value:"全部"}]
            this.languageList = [{value:"全部"}]
            this.databaseList = [{value:"全部"}]
            this.classifyList = [{value:"全部"}]
            for (let i = 0; i <response.data.degree['HoleType'].length ; i++) {
              this.degreeList.push({"value":response.data.degree['HoleType'][i]})
            }
            for (let i = 0; i <response.data.degree['devLanguage'].length ; i++) {
              this.languageList.push({"value":response.data.degree['devLanguage'][i]})
            }
            for (let i = 0; i <response.data.degree['devDatabase'].length ; i++) {
              this.databaseList.push({"value":response.data.degree['devDatabase'][i]})
            }
            for (let i = 0; i <response.data.degree['devClassify'].length ; i++) {
              this.classifyList.push({"value":response.data.degree['devClassify'][i]})
            }
            for (let i = 0; i <this.listdata.length ; i++) {
              this.listdata[i].status.start_flag = false
              this.listdata[i].status.stop_flag = false
              this.listdata[i].status.delete_flag = false
            }
            this.loading=false
            if (this.user.greenhand === true){
              if (this.page.total === 0){
                this.$message({
                  message:  "当前没有入门镜像，请联系管理员",
                  type: "warning",
                })
              }
              if (this.loading === false && this.firstLogin === false){
                this.$nextTick(() => {
                  this.showTips()
                  this.firstLogin = true
               });
              }
            }
          })
      },
      getselectdata(){
        const loading = this.$loading({
          lock: true,
          text: "Loading",
          // spinner: "el-icon-loading",
          background: "rgba(255,255,255,0.4)",
          target: document.querySelector("#first-bmh3")
        });
        let allTag = []
        allTag = allTag.concat(this.allTag5,this.allTag2,this.allTag3,this.allTag4)
        this.search = ''
          if (this.activeName === "started"){
            ImgDashboard(this.search,undefined,undefined,true,allTag,this.searchRank,this.activeName).then(response =>{

              this.startedlistdata = response.data.results
              this.page.total2 = response.data.count;
              for (let i = 0; i <this.startedlistdata.length ; i++) {
                this.startedlistdata[i].status.start_flag = false
                this.startedlistdata[i].status.stop_flag = false
                this.startedlistdata[i].status.delete_flag = false
              }
              loading.close()
            })
          }else {
          ImgDashboard(this.search,undefined,undefined,true,allTag,this.searchRank,this.activeName).then(response =>{
              this.listdata = response.data.results
              this.page.total1 = response.data.count;
              for (let i = 0; i <this.listdata.length ; i++) {
                this.listdata[i].status.start_flag = false
                this.listdata[i].status.stop_flag = false
                this.listdata[i].status.delete_flag = false
              }
            loading.close()
          })
        }
      },
      open(id,images_name,images_desc,status,container_id,raw_data) {
        this.images_id = ""
        this.images_name = ""
        this.images_desc = ""
        this.container_id = ""
        this.item_raw_data = ""
        this.vul_host = ""
        this.startCon = "loading"
        this.cStatus = true
        this.item_raw_data = raw_data
        this.images_id = id
        this.images_name = images_name
        this.images_desc = images_desc
        this.is_flag = raw_data.is_flag
        this.writeup_date = raw_data.writeup_date
        this.writeup_date_name = raw_data.writeup_date_name
        // this.is_docker_compose = raw_data.is_docker_compose
        this.centerDialogVisible = true
        this.open_flag = false
        if(this.open_flag === false){
          this.$set(raw_data.status, "start_flag", true)
        }
        this.$forceUpdate();
        if(raw_data.status.is_check === true){
          this.$message({
            message:  "该题目已经通过，重复答题分数不会累计",
            type: "success",
          })
          // this.centerDialogVisible = false
        }
        if (raw_data.status.status === "running"){
          this.images_id = raw_data.image_id
          this.vul_host = raw_data.status.host
          this.vul_port = JSON.parse(raw_data.status.port)
          this.container_id = raw_data.status.container_id
          this.startCon = false
          this.cStatus = false
          this.writeup_date = raw_data.writeup_date
          // this.writeup_date_name = raw_data.writeup_date_name
          this.is_docker_compose = raw_data.is_docker_compose
          this.is_flag = raw_data.is_flag
          if (this.user.greenhand === true){
                this.$nextTick(() => {
                  this.openDrawer()
             })
          }
        }else{
          ContainerSTART(id).then(response=>{
          let taskId = response.data["data"]
          let tmpRunContainerInterval = window.setInterval(() => {
            setTimeout(()=>{
              getTask(taskId).then(response=>{
                let responseStatus = response.data["status"]
                let responseData = response.data
                if (responseStatus === 1001){
                  // 一直轮训
                }else{
                  clearInterval(tmpRunContainerInterval)
                  raw_data.status.start_flag = false
                  if (responseStatus === 200){
                    container_id = responseData["data"]["id"]
                    this.container_id = container_id
                    this.vul_host = responseData["data"]["host"]
                    this.vul_port = responseData["data"]["port"]
                    raw_data.status.now = responseData["data"]["_now"]
                    raw_data.status.start_date = responseData["data"]["start_date"]
                    raw_data.status.end_date = responseData["data"]["end_date"]
                    raw_data.status.status = responseData["data"]["status"]
                    raw_data.status.container_id = container_id
                    this.startCon = false
                    this.cStatus = false
                    this.images_id = raw_data.image_id
                    if (this.user.greenhand === true){
                        this.$nextTick(() => {
                          this.openDrawer()
                     })
                  }
                  }else if (responseStatus === 201){
                    this.$message({
                      message: response.data["msg"],
                      type: "error",
                    })
                    this.listData(1)
                    this.timeData()
                    this.centerDialogVisible = false
                  }else{
                    this.$message({message:  response.data["msg"],
                      type: "error",
                    })
                    this.listData(1)
                    this.timeData()
                    this.centerDialogVisible = false
                  }
                }
              })
            },1)
          },2000)
        })
        }
      },
      subFlag(id,flag) {
          SubFlag(id,flag).then(response => {
            this.input = ""
            let responseData = response.data
            if(responseData["status"] === 200){
              this.$message({
                message:  "恭喜！通过",
                type: "success",
              })
              this.$store.state.user.greenhand = false
              this.open_flag = true
              this.centerDialogVisible = false
            }else if(responseData.status === 201){
              this.$message({
                message: responseData["msg"],
                type: "error",
              })
            }else{
              this.$message({
                message:  responseData["msg"],
                type: "error",
              })
            }
            this.item_raw_data.status.status = 'stop'
            this.item_raw_data.status.start_flag = false
          })
      },
      stop(container_id,raw,expire) {
        /**
         * 停止容器运行
         */
        this.$set(raw.status, "stop_flag", true)
        this.$forceUpdate();
        get_container_status(container_id).then(response=>{
          if(response.data.code===200 && response.data.status==="stop"){
            this.$message({
              message:'停止成功',
              type:'success'
            })
            raw.status.stop_flag = false;
            raw.status.start_date = "";
            raw.status.end_date = "";
            let allTag = []
            allTag = allTag.concat(this.allTag5,this.allTag2,this.allTag3,this.allTag4)
            if(allTag.length > 0 || this.searchRank !== 0 || this.search !== ""){
              // 获取当前所有分页的最后一页
              let all_page = parseInt(this.page.total/this.page.size);
              // 判断当前页面中是否只有一个镜像并且是否为最后一页
              if(this.listdata.length === 1 && this.current_page === all_page+1 && this.current_page > 1){
                this.current_page -= 1;
                if (this.activeName === "started"){
                  ImgDashboard(this.search,undefined,this.current_page,true,allTag,this.searchRank,this.activeName).then(response => {
                    this.startedlistdata = response.data.results
                    this.page.total2 = response.data.count;
                  })
                }else {
                  ImgDashboard(this.search,undefined,this.current_page,true,allTag,this.searchRank,this.activeName).then(response => {
                    this.listdata = response.data.results
                    this.page.total1 = response.data.count;
                  })
                }
              }
              else {
                if (this.activeName === "started"){
                  ImgDashboard(this.search,undefined,this.current_page,true,allTag,this.searchRank,this.activeName).then(response => {
                    this.startedlistdata = response.data.results
                    this.page.total2 = response.data.count;
                  })
                }else {
                  ImgDashboard(this.search,undefined,this.current_page,true,allTag,this.searchRank,this.activeName).then(response => {
                    this.listdata = response.data.results
                    this.page.total1 = response.data.count;
                  })
                }
              }
            }
            else {
              // 获取当前所有分页的最后一页
              let all_page = parseInt(this.page.total/this.page.size);
              // 判断当前页面中是否只有一个镜像并且是否为最后一页
              if(this.listdata.length === 1 && this.current_page===all_page+1 && this.current_page > 1){
                this.current_page -= 1;
                if (this.activeName === "started"){
                  ImgDashboard(undefined,undefined,this.current_page,undefined,allTag,undefined,this.activeName).then(response => {
                    this.startedlistdata = response.data.results
                    this.page.total2 = response.data.count;
                  })
                }else {
                  ImgDashboard(undefined,undefined,this.current_page,undefined,allTag,undefined,this.activeName).then(response => {
                    this.listdata = response.data.results
                    this.page.total1 = response.data.count;
                  })
                }
              }
              else {
                if (this.activeName === "started"){
                  ImgDashboard(undefined,undefined,this.current_page,undefined,allTag,undefined,this.activeName).then(response => {
                    this.startedlistdata = response.data.results
                    this.page.total2 = response.data.count;
                  })
                }else {
                  ImgDashboard(undefined,undefined,this.current_page,undefined,allTag,undefined,this.activeName).then(response => {
                    this.listdata = response.data.results
                    this.page.total1 = response.data.count;
                  })
                }
              }
            }
          }
          else if(response.data.code===200 && response.data.status==="delete"){
            this.$message({
              message:'停止成功',
              type:'success'
            })
            raw.status.stop_flag = false;
            raw.status.start_date = "";
            raw.status.end_date = "";
            raw.status.delete_flag = false;
            let allTag = []
            allTag = allTag.concat(this.allTag5,this.allTag2,this.allTag3,this.allTag4)
            if(allTag.length > 0 || this.searchRank !== 0 || this.search !== ""){
              // 获取当前所有分页的最后一页
              let all_page = parseInt(this.page.total/this.page.size);
              // 判断当前页面中是否只有一个镜像并且是否为最后一页
              if(this.listdata.length === 1 && this.current_page === all_page+1 && this.current_page > 1){
                this.current_page -= 1;
                if (this.activeName === "started"){
                  ImgDashboard(this.search,undefined,this.current_page,true,allTag,this.searchRank,this.activeName).then(response => {
                    this.startedlistdata = response.data.results
                    this.page.total2 = response.data.count;
                  })
                }else {
                  ImgDashboard(this.search,undefined,this.current_page,true,allTag,this.searchRank,this.activeName).then(response => {
                    this.listdata = response.data.results
                    this.page.total1 = response.data.count;
                  })
                }
              }
              else {
                if (this.activeName === "started"){
                  ImgDashboard(this.search,undefined,this.current_page,true,allTag,this.searchRank,this.activeName).then(response => {
                    this.startedlistdata = response.data.results
                    this.page.total2 = response.data.count;
                  })
                }else {
                  ImgDashboard(this.search,undefined,this.current_page,true,allTag,this.searchRank,this.activeName).then(response => {
                    this.listdata = response.data.results
                    this.page.total1 = response.data.count;
                  })
                }
              }
            }
            else {
              // 获取当前所有分页的最后一页
              let all_page = parseInt(this.page.total/this.page.size);
              // 判断当前页面中是否只有一个镜像并且是否为最后一页
              if(this.listdata.length === 1 && this.current_page === all_page+1 && this.current_page > 1){
                this.current_page -= 1;
                if (this.activeName === "started"){
                  ImgDashboard(undefined,undefined,this.current_page,undefined,allTag,undefined,this.activeName).then(response => {
                    this.startedlistdata = response.data.results
                    this.page.total2 = response.data.count;
                  })
                }else {
                  ImgDashboard(undefined,undefined,this.current_page,undefined,allTag,undefined,this.activeName).then(response => {
                    this.listdata = response.data.results
                    this.page.total1 = response.data.count;
                  })
                }
              }
              else {
                if (this.activeName === "started"){
                  ImgDashboard(undefined,undefined,this.current_page,undefined,allTag,undefined,this.activeName).then(response => {
                    this.startedlistdata = response.data.results
                    this.page.total2 = response.data.count;
                  })
                }else {
                  ImgDashboard(undefined,undefined,this.current_page,undefined,allTag,undefined,this.activeName).then(response => {
                    this.listdata = response.data.results
                    this.page.total1 = response.data.count;
                  })
                }
              }
            }
          }
          else if(response.data.code === 200 && response.data.status === "running"){
            ContainerStop(container_id,expire).then(response=>{
            let taskId = response.data["data"]
            let tmpStopContainerInterval = window.setInterval(() => {
              setTimeout(() => {
                getTask(taskId).then(response => {
                  let responseStatus = response.data["status"]
                  let responseData = response.data
                  if (responseStatus === 1001) {
                    // 一直轮训
                  } else {
                    clearInterval(tmpStopContainerInterval)
                    if (responseStatus === 200) {
                      this.$message({
                        message: responseData["msg"],
                        type: "success",
                      })
                      raw.status.status = "stop"
                      raw.status.start_date = ""
                      raw.status.end_date = ""
                      raw.status.stop_flag = false
                      let allTag = []
                      allTag = allTag.concat(this.allTag5,this.allTag2,this.allTag3,this.allTag4)
                        if(allTag.length > 0 || this.searchRank !== 0 || this.search !== ""){
                          // 获取当前所有分页的最后一页
                          let all_page = parseInt(this.page.total/this.page.size);
                          // 判断当前页面中是否只有一个镜像并且是否为最后一页
                          if(this.listdata.length === 1 && this.current_page === all_page && this.current_page > 1){
                            this.current_page -= 1;
                            if (this.activeName === "started"){
                              ImgDashboard(this.search,undefined,this.current_page,true,allTag,this.searchRank,this.activeName).then(response => {
                                this.startedlistdata = response.data.results
                                this.page.total2 = response.data.count;
                              })
                            }else {
                              ImgDashboard(this.search,undefined,this.current_page,true,allTag,this.searchRank,this.activeName).then(response => {
                                this.listdata = response.data.results
                                this.page.total1 = response.data.count;
                              })
                            }
                          }
                          else {
                            if (this.activeName === "started"){
                              ImgDashboard(this.search,undefined,this.current_page,true,allTag,this.searchRank,this.activeName).then(response => {
                                this.startedlistdata = response.data.results
                                this.page.total2 = response.data.count;
                              })
                            }else {
                              ImgDashboard(this.search,undefined,this.current_page,true,allTag,this.searchRank,this.activeName).then(response => {
                                this.listdata = response.data.results
                                this.page.total1 = response.data.count;
                              })
                            }
                          }
                        }
                      else {
                        // 获取当前所有分页的最后一页
                        let all_page = parseInt(this.page.total/this.page.size);
                        // 判断当前页面中是否只有一个镜像并且是否为最后一页
                        if(this.listdata.length === 1 && this.current_page === all_page && this.current_page > 1){
                          this.current_page -= 1;
                            if (this.activeName === "started"){
                              ImgDashboard(this.search,undefined,this.current_page,true,allTag,this.searchRank,this.activeName).then(response => {
                              this.startedlistdata = response.data.results
                              this.page.total2 = response.data.count;
                              })
                            }else {
                              ImgDashboard(this.search,undefined,this.current_page,true,allTag,this.searchRank,this.activeName).then(response => {
                              this.listdata = response.data.results
                              this.page.total1 = response.data.count;
                            })
                          }
                        }
                        else {
                          if (this.activeName === "started"){
                            ImgDashboard(this.search,undefined,this.current_page,true,allTag,this.searchRank,this.activeName).then(response => {
                              this.startedlistdata = response.data.results
                              this.page.total2 = response.data.count;
                            })
                          }else {
                            ImgDashboard(this.search,undefined,this.current_page,true,allTag,this.searchRank,this.activeName).then(response => {
                              this.listdata = response.data.results
                              this.page.total1 = response.data.count;
                            })
                          }
                        }
                      }
                    } else {
                      this.$message({
                        message: responseData["msg"],
                        type: "error",
                      })
                    }
                  }
                })
              }, 1)
            }, 2000)
        })
          }
        })
      },
      deleteContainer(container_id,raw){
        /**
         * 删除容器
         */
        this.$set(raw.status, "delete_flag", true)
        this.$set(raw.status, "stop_flag", true)
        this.$forceUpdate();
        ContainerDelete(container_id).then(response=>{
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
                  raw.status.delete_flag = false
                  if (responseStatus === 200){
                    // 清空状态码
                    raw.status.status = ""
                    // 清空 image_id
                    this.images_id = ""
                    // 清空 image_name
                    this.images_name = ""
                    // 清空 image_desc
                    this.images_desc = ""
                    // 清空 container_id
                    this.container_id = ""
                    // 清空 item_raw_data
                    this.item_raw_data = ""
                    raw.status.container_id = ""
                    this.$message({
                      message: responseData["msg"],
                      type: "success",
                    })
                    let allTag = []
                    allTag = allTag.concat(this.allTag5,this.allTag2,this.allTag3,this.allTag4)
                    if(allTag.length > 0 || this.searchRank !== 0 || this.search !== ""){
                      // 获取当前所有分页的最后一页
                      let all_page = parseInt(this.page.total/this.page.size);
                      // 判断当前页面中是否只有一个镜像并且是否为最后一页
                      if(this.listdata.length === 1 && this.current_page === all_page+1 && this.current_page > 1){
                        this.current_page -= 1;
                        if (this.activeName === "started"){
                          ImgDashboard(this.search,undefined,this.current_page,true,allTag,this.searchRank,this.activeName).then(response => {
                            this.startedlistdata = response.data.results
                            this.page.total2 = response.data.count;
                          })
                        }else {
                          ImgDashboard(this.search,undefined,this.current_page,true,allTag,this.searchRank,this.activeName).then(response => {
                            this.listdata = response.data.results
                            this.page.total1 = response.data.count;
                          })
                        }
                      }
                      else {
                        if (this.activeName === "started"){
                          ImgDashboard(this.search,undefined,this.current_page,true,allTag,this.searchRank,this.activeName).then(response => {
                            this.startedlistdata = response.data.results
                            this.page.total2 = response.data.count;
                          })
                        }else {
                          ImgDashboard(this.search,undefined,this.current_page,true,allTag,this.searchRank,this.activeName).then(response => {
                            this.listdata = response.data.results
                            this.page.total1 = response.data.count;
                          })
                        }
                      }
                    }
                    else {
                      let all_page = parseInt(this.page.total/this.page.size);
                      if(this.listdata.length === 1 && this.current_page === all_page+1 && this.current_page > 1){
                        this.current_page -= 1;
                        if (this.activeName === "started"){
                          ImgDashboard(undefined,undefined,this.current_page,undefined,allTag,undefined,this.activeName).then(response => {
                            this.startedlistdata = response.data.results
                            this.page.total2 = response.data.count;
                          })
                        }else {
                          ImgDashboard(undefined,undefined,this.current_page,undefined,allTag,undefined,this.activeName).then(response => {
                            this.listdata = response.data.results
                            this.page.total1 = response.data.count;
                          })
                        }
                      }
                      else {
                        if (this.activeName === "started"){
                          ImgDashboard(undefined,undefined,this.current_page,undefined,allTag,undefined,this.activeName).then(response => {
                            this.startedlistdata = response.data.results
                            this.page.total2 = response.data.count;
                          })
                        }else {
                          ImgDashboard(undefined,undefined,this.current_page,undefined,allTag,undefined,this.activeName).then(response => {
                            this.listdata = response.data.results
                            this.page.total1 = response.data.count;
                          })
                        }
                      }
                    }
                  }else{
                    this.$message({
                      message: responseData["msg"],
                      type: "error",
                    })
                  }
                }
              })
            },1)
          },2000)
        })
    },
      handleQuery(page){
        const loading = this.$loading({
          lock: true,
          text: "Loading",
          // spinner: "el-icon-loading",
          background: "rgba(255,255,255,255.4)",
          target: document.querySelector("#first-bmh3")
        });
        this.current_page = page
        let allTag = []
        allTag = allTag.concat(this.allTag5,this.allTag2,this.allTag3,this.allTag4)
        if (this.activeName === "started"){
          ImgDashboard(this.search,false,page,true,allTag,this.searchRank,this.activeName).then(response => {
              this.startedlistdata = response.data.results
              this.page.total2 = response.data.count;
            loading.close()
          })
        }else {
          ImgDashboard(this.search,false,page,true,allTag,this.searchRank,this.activeName).then(response => {
            this.listdata = response.data.results
            this.page.total1 = response.data.count;
            loading.close()
          })
        }
      },
      autoStop(){
        stoptimetemp().then(response => {
          const data = response.data;
          let msgType = 'success';
          let msg = '';
          if('2000'===data.code){
            msg = '计时模式已经关闭！'
          }else{
            msgType = 'error';
            msg = '关闭失败,内部错误';
          }
          this.$message({
            type: msgType,
            message: msg,
          });
        })
    },
      handleDialogClose(){
        if(this.open_flag === true){
          return
        }
        let allTag = []
        allTag = allTag.concat(this.allTag5,this.allTag2,this.allTag3,this.allTag4)
        if(allTag.length > 0 || this.searchRank !== 0 || this.search !== ""){
          if (this.activeName === "started"){
            ImgDashboard(this.search,undefined,this.current_page,true,allTag,this.searchRank,this.activeName).then(response => {
              this.startedlistdata = response.data.results
              this.page.total2 = response.data.count;
            })
          }else {
            ImgDashboard(this.search,undefined,this.current_page,true,allTag,this.searchRank,this.activeName).then(response => {
              this.listdata = response.data.results
              this.page.total1 = response.data.count;
            })
          }
        }
        else {
          if (this.activeName === "started"){
            ImgDashboard(undefined,undefined,this.current_page,undefined,allTag,undefined,this.activeName).then(response => {
              this.startedlistdata = response.data.results
              this.page.total2 = response.data.count
            })
          }else {
            ImgDashboard(undefined,undefined,this.current_page,undefined,allTag,undefined,this.activeName).then(response => {
              this.listdata = response.data.results
              this.page.total1 = response.data.count
            })
          }
        }
      },
      closeDrawer(done){
        this.drawer=false
      },
      openDrawer(){
        getWriteup(this.images_id).then(response => {
          if (response.data.code === 200){
            this.writeup_date = response.data.data.writeup_date
            this.writeup_date_name = response.data.data.username
            this.drawer=true
          }else {
          }
        })
      },
      editorButton(){
        this.drawerFlag=true
      },
      closeEditorButton(){
        this.drawerFlag=false
      },
      showTips(){
        const driver = new Driver({
          prevBtnText:"上一步",
          nextBtnText:"下一步",
          doneBtnText:"完成",
          closeBtnText:"关闭",
          // opacity:0,
          allowClose:false,
        });
        const steps = [
        {
          element:"#first-bmh3", // 这是点击触发的id
          popover:{
            title:"提示",
            description:"启动入门镜像,启动后可以点击镜像信息旁的<i  class=\"el-icon-reading\"  style=\"color: rgb(140, 197, 255);font-size: 20px\"></i>了解漏洞镜像！成功提交flag后可以解除新手模式，查看所有漏洞环境",
            position: "top",
          },
        },
      ];
        driver.defineSteps(steps);
        driver.start();
      },
      startloading(){
        const loading = this.$loading({
          lock: true,
          text: "Loading",
          // spinner: "el-icon-loading",
          background: "rgba(0,0,0,0.7)",
          target: document.querySelector("#first-bmh3")
        });
      },
      getUser() {
      this.user = {
        greenhand:this.greenhand
      }
      },
      showactive(tag){
        let tags = tag
        if (tags === "taglength2"){
          if (!this.showBtnTag2){
            this.taglength2 = 10
          }else {
            this.taglength2 = this.languageList.length
          }
          this.showBtnTag2 = !this.showBtnTag2;
        }
        if (tags === "taglength3"){
          if (!this.showBtnTag3){
            this.taglength3 = 10
          }else {
            this.taglength3 = this.degreeList.length
          }
          this.showBtnTag3 = !this.showBtnTag3;
        }
        if (tags === "taglength4"){
          if (!this.showBtnTag4){
            this.taglength4 = 10
          }else {
            this.taglength4 = this.classifyList.length
          }
          this.showBtnTag4 = !this.showBtnTag4;
        }
        if (tags === "taglength5"){
          if (!this.showBtnTag5){
            this.taglength5 = 10
          }else {
            this.taglength5 = this.databaseList.length
          }
          this.showBtnTag5 = !this.showBtnTag5;
        }
      },
      selectLan(index,item){
        this.current_page = 1
        this.activeClass2 = index
        this.allTag2.splice(0,1)
        if (item.value === "全部"){
        }else {
          this.allTag2.push(item.value)
        }
        this.getselectdata()
      },
      selectIfy(index,item){
        this.current_page = 1
        this.activeClass4 = index
        this.allTag4.splice(0,1)
        if (item.value === "全部"){
        }else {
          this.allTag4.push(item.value)
        }
        this.getselectdata()
      },
      selectDiff(index,item){
        this.current_page = 1
        this.activeClass1 = index
        this.searchRank = item.value
        this.getselectdata()
      },
      selectDeg(index,item){
        this.current_page = 1
        this.activeClass3 = index
        this.allTag3.splice(0,1)
        if (item.value === "全部"){
        }else {
          this.allTag3.push(item.value)
        }
        this.getselectdata()
      },
      selectSql(index,item){
        this.current_page = 1
        this.activeClass5 = index
        this.allTag5.splice(0,1)
        if (item.value === "全部"){
        }else {
          this.allTag5.push(item.value)
        }
        this.getselectdata()
      },
      currentTabs(tab, event){
        this.activeName = tab.name;
        this.changetableinit();
        let allTag = [];
        allTag = allTag.concat(this.allTag5,this.allTag2,this.allTag3,this.allTag4);
        if(allTag.length > 0 || this.searchRank !== 0 || this.search !== ""){
          if (this.activeName==='started'){
            ImgDashboard(this.search,undefined,this.current_page,true,allTag,this.searchRank,this.activeName).then(response => {
              this.startedlistdata = response.data.results
              this.page.total2 = response.data.count;
              this.loading=false
            })
          }else {
            ImgDashboard(this.search,undefined,this.current_page,true,allTag,this.searchRank,this.activeName).then(response => {
              this.listdata = response.data.results
              this.page.total1 = response.data.count;
              this.loading=false
            })
          }
        }
        else{
          if (this.activeName==='started'){
            ImgDashboard(undefined,undefined,this.current_page,undefined,allTag,undefined,this.activeName).then(response => {
              this.startedlistdata = response.data.results
              this.page.total2 = response.data.count;
              this.loading=false
            })
          }else {
            ImgDashboard(undefined,undefined,this.current_page,undefined,allTag,undefined,this.activeName).then(response => {
              this.listdata = response.data.results
              this.page.total1 = response.data.count;
              this.loading=false
            })
          }
        }
      },
  },
  mounted: function() {
      var _this = this;
      let yy = new Date().getFullYear();
      let mm = new Date().getMonth()+1;
      let dd = new Date().getDate();
      let hh = new Date().getHours();
      let mf = new Date().getMinutes()<10 ? '0'+new Date().getMinutes() : new Date().getMinutes();
      let ss = new Date().getSeconds()<10 ? '0'+new Date().getSeconds() : new Date().getSeconds();
      _this.get_time = yy+'-'+mm+'-'+dd+' '+hh+':'+mf+':'+ss;
  },
}

</script>

<style lang="scss" scoped>
.dashboard {
  &-container {
    margin: 30px;
  }
  &-text {
    font-size: 30px;
    line-height: 46px;
  }
}
.time {
  font-size: 13px;
  color: #999;
}

.bottom {
  margin-top: 5px;
  margin-bottom: 13px;
  line-height: 12px;
}

.button {
  padding: 5px;
  float: right;
}

.image {
  width: 100%;
  display: block;
}

.clearfix:before,
.clearfix:after {
  display: table;
  content: "";
}

.clearfix:after {
  clear: both
}

.text {
  font-size: 14px;
}

.item {
  margin-bottom: 18px;
}

.container-title{
  width: 100%;    /*根据自己项目进行定义宽度*/
  overflow: hidden;     /*设置超出的部分进行影藏*/
  text-overflow: ellipsis;     /*设置超出部分使用省略号*/
  white-space:nowrap ;    /*设置为单行*/
}

.date {

}
.date p{
  height: 20px;
  line-height: 20px;
  margin: 0;

  margin-block-end: 0em;
}

.el-row {
  display: flex;
  flex-wrap: wrap;
}

</style>

<style rel="stylesheet/scss" lang="scss">
.filter-line {
  padding: 13px 16px;
  box-sizing: border-box;
  display: flex;
  font-size: 14px;
  border-bottom: 1px dashed #dde6f0;
  background: #fff;

  .filter-name {
   width: 150px;
   height: 24px;
   text-align: center;
   line-height: 24px;
   color: #fff;
   background: #36a3f7;
   border-radius: 200px 0 200px 200px;
   margin-right: 20px;
  }
  .filter-content {
    display: flex;
    flex-flow: wrap;
    /*justify-content: space-between;*/
    align-items: center;
    flex-wrap: wrap;
    color: #656666;
    width: 90%;
  }
  span {
    display: inline-block;
    padding: 5px 20px;
    box-sizing: border-box;
    cursor: pointer;
    flex-wrap: wrap;
  }
  span.current {
   color: #126ef7;
   background: #ebf5ff;
   border-radius: 200px;
  }
}


.el-drawer{
  overflow: scroll
}
</style>
