<template>
  <div class="app-container">
    <el-row>
      <el-col :span="16">
        <el-card v-loading="loadingFlag" :element-loading-text="loadingText">
          <div slot="header" class="clearfix">
            <span>场景信息</span>
            <el-tooltip v-if="!isRun" content="运行中">
              <i style="color: #20a0ff;" class="el-icon-loading"></i>
            </el-tooltip>
            <el-tooltip v-if="isRun" content="未启动">
              <i class="fa fa-stop" aria-hidden="true"></i>
            </el-tooltip>
          </div>
          <el-container>
            <el-aside width="356px">
              <img v-if="layout.image_name !==imgpath" :src="layout.image_name"  alt="" width="356px" height="248px"/>
            </el-aside>
            <el-main style="margin-top: -15px">
              <el-row>
                <el-col :span="19">
                  <span class="info2">{{layout.name}}</span>
                </el-col>
              </el-row>
              <el-row style="margin-top: 15px">
                <el-col :span="5">
                  <span class="info3">难易程度</span>
                </el-col>
                <el-col :span="19">
                  <el-rate v-model="difvalue" disabled show-score text-color="#ff9900" score-template="{value}"></el-rate>
                </el-col>
              </el-row>
              <el-row style="margin-top: 20px">
                <el-col :span="5">
                  <span class="info3">当前进度</span>
                </el-col>
                <el-col :span="19">
                  <el-progress :text-inside="true" :stroke-width="20" color="rgba(64, 158, 255, 1)" style="width: 90%;color: #2a58e8" :percentage="parseFloat(currentProgress)" status="success"></el-progress>
                </el-col>
              </el-row>
              <el-row style="margin-top: 20px">
                <el-col :span="5">
                  <span class="info3">当前排名</span>
                </el-col>
                <el-col :span="19">
                  <span v-if="currentRank === 0" >
                    未上榜
                  </span>
                  <span v-else-if="currentRank > 0" >
                    {{currentRank}}
                  </span>
                </el-col>
              </el-row>
              <el-row style="margin-top: 20px">
                <el-col :span="5">
                  <span class="info3" style="margin-bottom: auto">Flag</span>
                </el-col>
                <el-col :span="19">
                  <el-input :disabled="isRun" size="small" style="width: 80%" v-model="flag" placeholder="请输入Flag：格式flag-{xxxxxxxx}"></el-input>
                  <el-button size="small" :disabled="isRun" style="color: rgba(64, 158, 255, 1)" type="text" @click="handleFlag">提交</el-button>
                </el-col>
              </el-row>
              <el-row style="margin-top: 12px">
                <el-button v-if="isAdmin===true && isRun" class="btn1" size="medium" @click="handleRun">
                  <span class="span1"><i class="el-icon-video-play" style="margin-right: 2px"></i>启动场景</span>
                </el-button>
                <el-button v-if="isAdmin===true && !isRun" class="btn1" size="small" @click="handleStop">
                  <span class="span1"><i class="el-icon-loading" style="margin-right: 2px"></i>停止场景</span>
                </el-button>
                该场景已有
                <span class="span5">{{adoptCount}}</span>
                人完成/
                <span class="span6">{{failCount}}</span>
                人未通过
              </el-row>
            </el-main>
            <el-aside width="60px">
              <el-row>
                <el-col>
                  <span class="txt8">{{currentScore}}</span>
                  <span class="word5">分</span>
                </el-col>
              </el-row>
            </el-aside>
          </el-container>
          <el-divider></el-divider>
          <el-container>
            <el-main>
              <el-row>
                <span class="span2">环境描述</span>
                <el-link v-if="isAdmin===true" @click="openDrawer" type="primary" size="mini">编辑</el-link>
              </el-row>
              <el-row>
                <div class="container" style="margin-top: 24px">
                  <ViewerEditor v-if="loadingData" v-model="scene_writeup_date" ref="viewerEditor1"  :options="{hideModeSwitch:true, previewStyle:'vertical'}"  height="500px" ></ViewerEditor>
                </div>
              </el-row>
              <el-row style="margin-top: 24px">
                <span class="span2">访问地址</span>
              </el-row>
              <el-row style="margin-top: 24px" v-for="(item,i) in open">
                <span class="span3" > {{item}} </span>
              </el-row>
            </el-main>
          </el-container>
        </el-card>
        <el-card style="margin-top: 20px;">
          <el-row>
            <el-col>
              <span>评论</span>
              <el-divider></el-divider>
              <el-input rows="5" type="textarea" placeholder="既然来了就说点什么吧～" v-model="contentText" maxlength="500" show-word-limit></el-input>
              <el-button size="small" @click="handleText" type="primary" style="float: right;margin-top: 10px">发表</el-button>
            </el-col>
          </el-row>
          <el-row >
            <el-col v-for="(item,index) in contentList" :key="index">
              <el-card style="margin-top: 10px">
              <el-container>
                <el-aside width="48px" style="margin-top: 7px">
                  <template>
                    <img :src="item.user_avatar" style="width: 48px;height: 48px;border-radius: 50%;float: left;margin-top: 10px">
                  </template>
                </el-aside>
                <el-main>
                  <el-row>
                    <el-col :span="3">
                      <span class="span7">
                        {{item.username}}
                      </span>
                    </el-col>
                    <el-col :span="20">
                      <span class="span8">
                        {{item.create_time}}
                      </span>
                    </el-col>
                  </el-row>
                  <el-row style="margin-top: 5px">
                    <span>{{item.content}}</span>
                     <el-button size="mini" v-if="isAdmin===true || userAuth===item.username" @click="delComment(item.comment_id)" style="float: right;margin-top: -5px">
                      删除
                     </el-button>
                  </el-row>
                </el-main>
              </el-container>
            </el-card>
            </el-col>
          </el-row>
        </el-card>
      </el-col>
      <el-col style="margin-left: 10px" :span="7">
        <el-card>
          <div slot="header" class="clearfix">
            <span>场景排名</span>
          </div>
          <div>
            <el-table :data="rankList">
<!--              <el-table-column label="序号" type="index" :index="computeTableIndex"></el-table-column>-->
              <el-table-column type="index" label="排名" width="100px">
                <template slot-scope="scope">
                  <p v-if="page.currentPageNum*page.size+scope.$index+1-page.size>=4" style="margin-left: 15px">{{page.currentPageNum*page.size+scope.$index+1-page.size}}</p>
                  <svg-icon icon-class="trophy1" v-if="page.currentPageNum*page.size+scope.$index+1-page.size===1"  style="margin-left: 15px;height: 48px"/>
                  <svg-icon icon-class="trophy2" v-if="page.currentPageNum*page.size+scope.$index+1-page.size===2"  style="margin-left: 15px;height: 48px"/>
                  <svg-icon icon-class="trophy3" v-if="page.currentPageNum*page.size+scope.$index+1-page.size===3"  style="margin-left: 15px;height: 48px"/>
                </template>
              </el-table-column>
              <el-table-column prop="username" :show-overflow-tooltip=true label="用户">
                <template slot-scope="scope">
                  <img :src="scope.row.user_avatar" style="width: 30px;height: 30px;border-radius: 50%;float: left;margin-top: 10px">
                  <p style="float: left;margin-left: 5px;margin-top: 14px">{{scope.row.username}}</p>
                </template>
              </el-table-column>
              <el-table-column prop="score" label="积分" width="80"></el-table-column>
            </el-table>
          </div>
          <div style="margin-top: 20px">
            <el-pagination
              :page-size="page.size"
              @current-change="handleRank"
              layout="total, prev, pager, next, jumper"
              :total="page.total">
            </el-pagination>
          </div>
        </el-card>
      </el-col>
    </el-row>
    <div style="margin-top: 20px">
    <el-dialog :visible.sync="dialogVisible" title="请输入验证码" width="400px">
      <el-form>
        <el-form-item>
          <el-row :span="24">
            <el-col :span="8">
              <el-input v-model="commentCode" auto-complete="off" placeholder="请输入验证码"></el-input>
            </el-col>
            <el-col :span="12">
              <div class="login-code">
                  <!--验证码组件-->
                  <v-sidentify @getIdentifyCode="identifyCode"></v-sidentify>
              </div>
            </el-col>
          </el-row>
          <el-row>
            <el-button type="primary" style="float: right" @click="commitText">确认</el-button>
          </el-row>
        </el-form-item>
      </el-form>
    </el-dialog>
    </div>
    <div style="margin-top: 20px">
      <el-drawer v-if="drawer" :visible="drawer" size="50%" :direction="derection" modal="false" append-to-body="true" :before-close="closeDrawer" >
        <div style="margin-right: 10px">
          <el-button icon="el-icon-edit-outline" size="small" style="position:absolute;z-index: 9999;right:60px;top: 21px;" @click="createSceneWriteup">修改</el-button>
        </div>
        <div>
          <el-row>
            <el-col :span="22" :offset="1">
              <div class="container">
                <markdown-editor ref="markdownEditor1" v-model="scene_update_date" :options="{hideModeSwitch:true, previewStyle:'vertical'}"  height="400px" />
              </div>
            </el-col>
          </el-row>
        </div>
      </el-drawer>
    </div>
  </div>
</template>

<script>

import { mapGetters } from 'vuex'
import {sceneGet, sceneStart, sceneStop,sceneFlag, sceneRank} from '@/api/scene'
import { commitComment, getComment, CommentDelete  } from '@/api/user'
import CountDown from "vue2-countdown";
import { updateLayoutDesc } from '@/api/layout'
import verification from "./verification";
import MarkdownEditor from '@/components/MarkdownEditor'
import ViewerEditor from '@/components/ViewerEditor'


export default {
  inject: ['reload'],
  name: 'timeindex.vue',
  data(){
    return {
      layout: {
        id: "",
        name: "",
        desc: "",
        image_name:"",
      },
      loadingFlag: true,
      loadingText: "环境启动中",
      flag: "",
      isAdmin: false,
      page:{
        total: 0,
        size: 20,
        page: 1,
        currentPageNum:1,
      },
      isRun: false,
      currentProgress: "",
      currentRank: 0,
      currentScore: 0,
      adoptCount: 0,
      failCount: 0,
      incompletePeple:0,
      open: [],
      rankList:[],
      scene_writeup_date:'',
      scene_update_date:'',
      drawer:false,
      drawerFlag:false,
      derection:"btt",
      imgpath:'/images/',
      difvalue: 3.5,
      contentText:"",
      contentList:[],
      dialogVisible:false,
      verificationCode:"",
      commentCode:"",
      loadingData:false,
      userAuth:"",
      loadingData:false,
    }
  },
  computed: {
    ...mapGetters([
      'name',
      'avatar',
      'roles',
      'rank'
    ])
  },
  created() {
    if (this.roles.length >0 &&this.roles[0] === "admin"){
      this.isAdmin = true
    }
    this.userAuth = this.name
    this.initModelInfo()
    this.handleRank(1)
    this.initComment()
  },
  components:{
    'v-sidentify':verification,
    MarkdownEditor,
    ViewerEditor,
  },
  methods:{
    identifyCode(data){
      this.verificationCode = data
    },
    /**
     * 初始化模式信息
     */
    initModelInfo(){
      this.loadingText = "模式信息初始化中"
      this.loadingFlag = true
      // 环境 id
      let layoutId = this.$route.query.layout_id
      if (layoutId === undefined || layoutId == null || layoutId === ""){
        this.$message({
          message: "参数不能为空",
          type: "error",
        })
        this.$router.push({path: "/scene/list"})
      }
      this.layout.id = layoutId
      sceneGet(layoutId).then(response=>{
        this.loadingFlag = false
        let rsp = response.data
        let status = rsp.status
        let msg = rsp.msg
        if (status === 200){
          this.layout.name = rsp.data["layout"]["name"]
          this.layout.desc = rsp.data["layout"]["desc"]
          this.scene_writeup_date = rsp.data["layout"]["desc"]
          this.loadingData = true
          if (!rsp.data["layout"]["image_name"]){
            this.layout.image_name = require("../../assets/modelbg.jpg")
          }else {
            // this.layout.image_name = require("../../assets/modelbg.jpg")
            this.layout.image_name = '/images/' + rsp.data["layout"]["image_name"]
          }
          this.open = rsp.data["open"]
          if(!rsp.data["is_run"]){
            this.isRun = true
          }
        }else{
          this.$message({
            message: msg,
            type: "error",
          })
        }
      }).catch(err => {
        this.loadingFlag = false
        this.$message({
          message: "服务器内部错误",
          type: "error",
        })
        this.$router.push({path: "/scene/list"})
      })
    },
    /**
     * 启动
     */
    handleRun(){
      this.loadingFlag = true
      this.loadingText= "模式启动中"
      let layoutId = this.layout.id
      if (layoutId === undefined || layoutId == null || layoutId === ""){
        this.$message({
          message: "参数不能为空",
          type: "error",
        })
        this.$router.push({path: "/scene/list"})
      }
      sceneStart(layoutId).then(response => {
        this.loadingFlag = false
        let rsp = response.data
        let status = rsp.status
        let msg = rsp.msg
        if (status === 200){
          this.layout.name = rsp.data["layout"]["name"]
          this.layout.desc = rsp.data["layout"]["desc"]
          this.open = rsp.data["open"]
          if (undefined === rsp.data["is_run"]){
            rsp.data["is_run"] = true
          }
          this.isRun = !rsp.data["is_run"]
          this.$message({
            message: "启动成功",
            type: 'success'
          })
        }else{
          this.$message({
            message: msg,
            type: "error",
          })
        }
      }).catch(err => {
        this.loadingFlag = false
        this.$message({
          message: "服务器内部错误",
          type: "error",
        })
        this.$router.push({path: "/scene/list"})
      })
    },
    /**
     * 停止
     */
    handleStop(){
      this.loadingFlag = true
      this.loadingText = "模式停止中"
      let layoutId = this.layout.id
      if (layoutId === undefined || layoutId == null || layoutId === ""){
        this.$message({
          message: "参数不能为空",
          type: "error",
        })
        this.$router.push({path: "/scene/list"})
      }
      sceneStop(layoutId).then(response => {
        this.loadingFlag = false
        let rsp = response.data
        let status = rsp.status
        let msg = rsp.msg
        if (status === 200){
          this.$message({
            message: "关闭成功",
            type: 'success'
          })
          this.initModelInfo()
        }else{
          this.$message({
            message: msg,
            type: "error",
          })
        }
      }).catch(err => {
        this.loadingFlag = false
        this.$message({
          message: "服务器内部错误",
          type: "error",
        })
      })
      // this.loadingFlag = false
    },
    /**
     * 提交flag
     */
    handleFlag(){
      let flag = this.flag
      this.loadingFlag = true
      this.loadingText = "Flag 提交中"
      if (flag === "" || flag === null){
        this.$message({
          message: "flag 不能为空",
          type: "error"
        })
        return
      }
      sceneFlag(this.layout.id, flag).then(response => {
        this.loadingFlag = false
        let rsp = response.data
        let status = rsp.status
        if (status === 200){
          this.$message({
            message:  "恭喜！通过",
            type: "success",
          })
          this.flag = ""
          this.handleRank(1)
        }else{
          this.$message({
            message:rsp.msg,
            type: "error"
          })
        }
      }).catch(err =>{
        this.loadingFlag = false
        this.$message({
          message: "服务器内部错误",
          type: "error",
        })
      })
    },
    /**
     * 初始化排行
     */
    handleRank(page){
      this.loadingFlag = true
      this.loadingText = "排行初始化中"
      this.page.page = page
      this.page.currentPageNum = page
      sceneRank(this.layout.id, page).then(response => {
        this.loadingFlag = false
        let rsp = response.data
        this.page.total = rsp.count
        this.rankList = rsp.result
        // 当前进度
        this.currentProgress = rsp.progress
        // 当前排名
        this.currentRank = rsp.current
        // 当前分数
        this.currentScore = rsp.score
        this.adoptCount = rsp.adopt_count
        this.failCount = this.page.total - this.adoptCount
      }).catch(err => {
        this.loadingFlag = false
        this.$message({
          message: "服务器内部错误",
          type: 'error'
        })
      })
    },
    computeTableIndex(index){
      return (this.page.page - 1) * this.page.size + index + 1
    },
    handleText(){
      this.dialogVisible = true
    },
    commitText(){
      if (this.commentCode===this.verificationCode) {
        let commentDict = new FormData()
        commentDict.set("scene_id", this.$route.query.layout_id)
        commentDict.set("content", this.contentText)
        commentDict.set("scene_type", "layout")
        commitComment(commentDict).then(response => {
          if (response.data.status === 200) {
            this.$message({
              message: response.data.message,
              type: "success",
            })
            this.dialogVisible = false
            this.reload()
          } else {
            this.$message({
              message: response.data.message,
              type: "error",
            })
          }
        })
      }else {
        this.$message({
          message: '验证码错误',
          type: "error",
        })
      }
    },
    initComment(){
      let sceneId = this.$route.query.layout_id
      getComment(sceneId).then(response=>{
        this.contentList = response.data.results
      })
    },
    delComment(id){
      CommentDelete(id).then(response=>{
        if (response.data.status === 200){
          this.$message({
            message: "删除成功",
            type: 'success'
          })
          this.initComment()
        }else {
          this.$message({
            message: response.data.msg,
            type: "error",
          })
        }
      })
    },
    closeDrawer(){
      this.drawer=false
      this.initModelInfo()
    },
    openDrawer(){
      this.scene_update_date = this.scene_writeup_date
      this.drawer=true
    },
    createSceneWriteup(){
      let sceneId = this.$route.query.layout_id
      let data = {"data":this.scene_update_date}
      updateLayoutDesc(sceneId,data).then(response=>{
        if (response.data.status === 200){
          this.$message({
            message: "编辑成功",
            type: 'success'
          })
          this.drawer = false
          this.reload()
        }else {
          this.$message({
            message: response.data.msg,
            type: 'error'
          })
        }
      })
    }
  }
}
</script>

<style scoped>
.clearfix:before,
.clearfix:after {
  display: table;
  content: "";
}
.clearfix:after {
  clear: both
}
.filter-tag {
 width: 120px;
 /*height: 24px;*/
 text-align: center;
 line-height: 20px;
 color: #fff;
 background: #685d5d;
 border-radius: 20px 20px 20px 20px;
 margin-right: 10px;
}
.info2 {
  width: 100px;
  height: 20px;
  font-size: 20px;
  color: #303133;
  line-height: 20px;
}

.info3 {
  width: 56px;
  height: 14px;
  font-size: 14px;
  color: rgba(48, 49, 51, 1);
  /*display: block;*/
  line-height: 14px;
}

.txt8 {
  font-size: 28px;
  color: rgba(64, 158, 255, 1);
  line-height: 28px;
  overflow: hidden;
  text-overflow: ellipsis;
}

.word5 {
  font-size: 12px;
  color: rgba(64, 158, 255, 1);
  line-height: 28px;
  overflow: hidden;
  text-overflow: ellipsis;
}
.btn1 {
  width: 145px;
  height: 42px;
  background: #409EFF;
  border-radius: 2px;
}
.span1 {
  width: 72px;
  height: 18px;
  font-size: 18px;
  font-weight: 400;
  color: #FFFFFF;
  line-height: 18px;
}
.span2 {
  width: 80px;
  height: 20px;
  font-size: 20px;
  color: #303133;
  line-height: 20px;
}
.span3 {
  width: 302px;
  height: 14px;
  font-size: 14px;
  color: #606266;
  line-height: 14px;
}
.span5 {
  font-size: 24px;
  color: rgba(1, 154, 39, 1);
  line-height: 24px;
  overflow: hidden;
  text-overflow: ellipsis;
}
.span6 {
  font-size: 24px;
  font-family: Helvetica-Bold;
  color: rgba(250, 63, 63, 1);
  line-height: 24px;
  overflow: hidden;
  text-overflow: ellipsis;
}
.span7{
  width: 87px;
  height: 14px;
  font-size: 16px;
  color: #303133;
  line-height: 14px;
}
.span8{
  width: 88px;
  height: 14px;
  font-size: 14px;
  color: #999999;
  line-height: 14px;

}
</style>
