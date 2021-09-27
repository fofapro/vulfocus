<template>
  <div class="app-container">
    <el-row>
      <el-col :span="16" v-for="(titem,index) in timelist" :key="index" >
        <el-card>
          <div slot="header" class="clearfix">
            <span>时间模式信息</span>
            <el-tooltip content="未启动" v-if="countlist.length ===0">
              <i class="fa fa-stop" aria-hidden="true"></i>
            </el-tooltip>
            <el-tooltip v-else-if="titem.temp_id === countlist[0].temp_time_id" content="运行中">
              <i style="color: #20a0ff;" class="el-icon-loading"></i>
            </el-tooltip>
          </div>
          <el-container>
            <el-aside width="356px">
              <img v-if="titem.image_name !==imgpath" :src="titem.image_name"  alt="" width="356px" height="248px"/>
            </el-aside>
            <el-main style="margin-top: -15px">
              <el-row>
                <el-col :span="19">
                  <span class="info2">{{titem.name}}</span>
                </el-col>
              </el-row>
              <el-row style="margin-top: 25px">
                <el-col :span="5">
                  <span class="info3">计时时间</span>
                </el-col>
                <el-col :span="19">
                  {{ titem.time_range }}分钟
                </el-col>
              </el-row>
              <el-row style="margin-top: 20px">
                <el-col :span="5">
                  <span class="info3">rank范围</span>
                </el-col>
                <el-col :span="19">
                  {{ titem.rank_range }}
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
                  <span class="info3">倒计时</span>
                </el-col>
                <el-col :span="19">
                  <count-down style="margin-top: -15px" v-if="countlist.length >0 && countlist[0].temp_time_id === titem.temp_id" v-on:end_callback="autostop()" :currentTime="countlist[0].start_date" :startTime="countlist[0].start_date" :endTime="countlist[0].end_date" :dayTxt="'天'" :hourTxt="'小时'" :minutesTxt="'分钟'" :secondsTxt="'秒'">
                  </count-down>
                  <span v-else >未开始</span>
                </el-col>
              </el-row>
              <el-row style="margin-top: 20px" v-if="countlist.length !==0">
                <el-button class="btn1" style="margin-top: -15px" size="mini" v-if="titem.temp_id!== countlist[0].temp_time_id" @click="handleOk(titem)" >
                  <span class="span1"><i class="el-icon-video-play" style="margin-right: 2px"></i>启动盲盒</span>
                </el-button>
                <el-button class="btn1" style="margin-top: -15px" size="mini" v-if="titem.temp_id === countlist[0].temp_time_id" @click="stop()">
                  <span class="span1"><i class="el-icon-loading" style="margin-right: 2px"></i>停止盲盒</span>
                </el-button>
              </el-row>
              <el-row style="margin-top: 20px" v-else-if="countlist.length===0">
                <el-col>
                  <el-button size="mini" class="btn1" @click="opendialog(titem)" >
                    <span class="span1"><i class="el-icon-video-play" style="margin-right: 2px"></i>启动盲盒</span>
                  </el-button>
                  该场景已有
                  <span class="span5">{{page.total}}</span>
                  人参加
                </el-col>
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
                <span class="span2">盲盒描述</span>
              </el-row>
              <el-row style="margin-top: 24px">
                <span class="span3"> {{ titem.time_desc }} </span>
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
            <span>时间模式排名</span>
          </div>
          <div>
            <el-table :data="tableData">
<!--              <el-table-column label="序号" type="index" :index="computeTableIndex" width="50"></el-table-column>-->
              <el-table-column type="index" label="排名" width="100px">
                <template slot-scope="scope">
                  <p v-if="page.currentPageNum*page.size+scope.$index+1-page.size>=4" style="margin-left: 15px">{{page.currentPageNum*page.size+scope.$index+1-page.size}}</p>
                  <svg-icon icon-class="trophy1" v-if="page.currentPageNum*page.size+scope.$index+1-page.size===1"  style="margin-left: 15px;height: 48px"/>
                  <svg-icon icon-class="trophy2" v-if="page.currentPageNum*page.size+scope.$index+1-page.size===2"  style="margin-left: 15px;height: 48px"/>
                  <svg-icon icon-class="trophy3" v-if="page.currentPageNum*page.size+scope.$index+1-page.size===3"  style="margin-left: 15px;height: 48px"/>
                </template>
              </el-table-column>
              <el-table-column prop="name" :show-overflow-tooltip=true label="用户名">
                <template slot-scope="scope">
                  <img :src="scope.row.avatar" style="width: 30px;height: 30px;border-radius: 50%;float: left;margin-top: 10px">
                  <p style="float: left;margin-left: 5px;margin-top: 14px">{{scope.row.name}}</p>
                </template>
              </el-table-column>
              <el-table-column prop="rank" label="积分" width="80"></el-table-column>
            </el-table>
          </div>
          <div style="margin-top: 20px">
            <el-pagination
              :page-size="page.size"
              @current-change="StateChange"
              time="total, prev, pager, next, jumper"
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
  </div>
</template>

<script>

import { mapGetters } from 'vuex'
import CountDown from 'vue2-countdown'
import { start,timetemplist,timeranklist,stoptimetemp,gettimetemp,publicMethod,sceneGetTemp } from '@/api/timemoudel'
import verification from "./verification";
import { commitComment, getComment } from '@/api/user'

export default {
  inject: ['reload'],
  name: 'timeindex.vue',
  components: {
    CountDown,
    'v-sidentify':verification
  },
  data(){
    return {
      search: "",
      get_time:"",
      timelist:[],
      countlist:[],
      tableData:[],
      imgpath: '/images/',
      modelimg: require("../../assets/modelbg.jpg"),
      page:{
        total: 0,
        size: 20,
        page: 1,
        currentPageNum:1,
      },
      currentRank:0,
      currentScore:0,
      rankList:[],
      contentText:"",
      contentList:[],
      dialogVisible:false,
      verificationCode:"",
      commentCode:"",
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
    this.templist()
    this.gettimelist()
    this.StateChange()
    this.initComment()
  },
  methods:{
    identifyCode(data){
      this.verificationCode = data
    },
    gettimelist(){
      gettimetemp().then(response => {
        let data = response.data.results
          this.countlist = data
          if (this.countlist.length===0){
          }else {
            this.countlist[0].end_date = publicMethod.getTimestamp(this.countlist[0].end_date)
            this.countlist[0].start_date = publicMethod.getTimestamp(this.get_time)
          }
        }
      )
    },
    templist(){
      let temp_id = this.$route.query.temp_id
      if (temp_id === undefined || temp_id == null || temp_id === ""){
        this.$message({
          message: "参数不能为空",
          type: "error",
        })
        this.$router.push({path: "/scene/list"})
      }
      sceneGetTemp(temp_id).then(response =>{
        let data = response.data
        if (!data.image_name){
            data.image_name = require("../../assets/modelbg.jpg")
          }else {
            // this.layout.image_name = require("../../assets/modelbg.jpg")
            data.image_name = '/images/' + data.image_name
          }
        this.timelist.push(data)
      })
    },
    stop(){
      this.$confirm('是否取消挑战?', '提示', {
        center: true,
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
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
        this.$router.push({ path: '/dashboard' })
      }).catch(() => {
        this.$message({
          type: 'info',
          message: '已取消'
        });
      });
    },
    opendialog(item){
      this.item = item
      if (item.flag_status===true){
        this.$message({
          type:"error",
          message:item.time_range + "分钟挑战赛已经开始"
        })
      }else{
      this.$confirm('是否开始挑战?', '提示', {
        center: true,
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        start(item).then(response => {
          const data = response.data;
          let msgType = 'success';
          let msg = '';
          if('200'===data.code){
            msg = '计时模式开始启动！'
          }else if ('2001' === data.code){
            msg = '计时模式已经启动，请勿重新启动'
          }else{
            msgType = 'error';
            msg = '内部错误';
          }
          this.$message({
            type: msgType,
            message: msg,
          });
        })
        this.$router.push({ path: '/dashboard' })
      }).catch(() => {
        this.$message({
          type: 'info',
          message: '已取消挑战'
        });
      });
    }},
    handleOk(titem){
      if (this.countlist.length!==0){
        this.$message({
          message: '已有时间模式在运行，请先关闭',
          type: 'error'
        })
        return
      }else{
        this.opendialog(titem)
      }
    },
    autostop(){
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
    StateChange(page){
      if(page == undefined || page == null || page == ""){page=1}
      let temp_id = this.$route.query.temp_id
      if (temp_id === undefined || temp_id == null || temp_id === ""){
        this.$message({
          message: "参数不能为空",
          type: "error",
        })
        this.$router.push({path: "/scene/list"})
      }
      timeranklist(temp_id,page).then(response => {
        this.tableData = response.data.results
        this.page.total = response.data.count
        this.currentScore = response.data.current_score
        this.currentRank = response.data.current_rank
        this.page.currentPageNum = page
      })
    },
    handleText(){
      this.dialogVisible = true
    },
    commitText(){
      if (this.commentCode===this.verificationCode) {
        let commentDict = new FormData()
        commentDict.set("scene_id", this.$route.query.temp_id)
        commentDict.set("content", this.contentText)
        commentDict.set("scene_type", "TimingBlindBox")
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
      let sceneId = this.$route.query.temp_id
      getComment(sceneId).then(response=>{
        this.contentList = response.data.results
      })
    }
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
  }
}
</script>

<style scoped>
.text {
  font-size: 14px;
}

.item {
  margin-bottom: 18px;
}
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
</style>
