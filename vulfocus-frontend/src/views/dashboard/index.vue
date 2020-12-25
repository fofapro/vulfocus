<template>

  <div class="dashboard-container">
    <el-dialog :visible.sync="centerDialogVisible" title="镜像信息" >
      <div class="text item" v-loading="startCon" element-loading-text="环境启动中">
        <div class="text item" >
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
        <el-form>
          <el-form-item label="Flag">
            <el-input v-model="input" placeholder="请输入Flag：格式flag-{xxxxxxxx}"></el-input>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="subFlag(container_id,input.trim())" :disabled="cStatus">提 交</el-button>
            <!--</div>-->
          </el-form-item>
        </el-form>
      </div>
    </el-dialog>
    <el-row :gutter="24" >
      <el-col>
        <el-input v-model="search" style="width: 230px;" size="medium"></el-input>
        <el-button class="filter-item" size="medium" style="margin-left: 10px;margin-bottom: 10px" type="primary" icon="el-icon-search" @click="handleQuery(1)">
          查询
        </el-button>
      </el-col>
      <el-col :span="6" v-for="(item,index) in listdata" :key="index"  style="padding-bottom: 18px;">
        <el-card :body-style="{ padding: '8px' }" shadow="hover"
                 @click.native=" item.status.status === 'running' && open(item.image_id,item.image_vul_name,item.image_desc,item.status.status,item.status.container_id,item)" >
          <div class="clearfix" >
            <div style="display: inline-block;height: 20px;line-height: 20px;min-height: 20px;max-height: 20px;">
              <svg-icon icon-class="bug"  style="font-size: 20px;"/>
              <el-tooltip v-if="(item.status.status === 'stop' || item.status.status === 'delete') && item.status.is_check === true" content="已通过" placement="top">
                <i style="color: #20a0ff;" class="el-icon-check"></i>
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
                <count-down style="display: inline-block;height: 20px;line-height: 20px;size: 20px;margin-block-start: 0em;margin-block-end: 0em;" v-on:end_callback="stop(item.status.container_id, item)" :currentTime="item.status.now" :startTime=item.status.now :endTime=item.status.end_date :secondsTxt="''"></count-down>
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
        :total="page.total">
      </el-pagination>
    </div>
  </div>
</template>

<script>
import { ImgList,SubFlag,ContainerSTART,ContainerDelete,ContainerStop } from '@/api/docker'
import { getTask } from '@/api/tasks'
import CountDown from 'vue2-countdown'
export default {
  name: 'Dashboard',
  components: {
    CountDown
  },
  replace:true,
  data() {
    return {
      page:{
        total: 0,
        size: 20,
      },
      listdata: [],
      vul_host: "",
      centerDialogVisible: false,
      startCon:false,
      startTime:(new Date()).getTime(),
      input: "",
      images_id: "",
      container_id: "",
      images_name: "",
      images_desc: "",
      item_raw_data: "",
      cStatus: true,
      search: "",
      vul_port:{}
      };
    },
  created() {
    this.listData(1)
  },
  methods:{
      listData() {
          ImgList().then(response => {
            this.listdata = response.data.results
            this.page.total = response.data.count
            for (let i = 0; i <this.listdata.length ; i++) {
              this.listdata[i].status.start_flag = false
              this.listdata[i].status.stop_flag = false
              this.listdata[i].status.delete_flag = false
            }
          })
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
        this.centerDialogVisible = true
        this.$set(raw_data.status, "start_flag", true)
        this.$forceUpdate();
        if(raw_data.status.is_check === true){
          this.$message({
            message:  "该题目已经通过，重复答题分数不会累计",
            type: "success",
          })
          // this.centerDialogVisible = false
        }
        if (raw_data.status.status === "running"){
          this.vul_host = raw_data.status.host
          this.vul_port = JSON.parse(raw_data.status.port)
          this.container_id = raw_data.status.container_id
          this.startCon = false
          this.cStatus = false
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
                  }else if (responseStatus === 201){
                    this.$message({
                      message: response.data["msg"],
                      type: "error",
                    })
                    this.centerDialogVisible = false
                  }else{
                    this.$message({message:  response.data["msg"],
                      type: "error",
                    })
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
              this.listData(1)
            }else if(responseData.status === 201){
              this.$message({
                message: responseData["msg"],
                type: "info",
              })
            }else{
              this.$message({
                message:  responseData["msg"],
                type: "error",
              })
            }
            this.centerDialogVisible = false
            this.item_raw_data.status.status = 'stop'
          })
      },
      stop(container_id,raw) {
        /**
         * 停止容器运行
         */
        this.$set(raw.status, "stop_flag", true)
        this.$forceUpdate();
        ContainerStop(container_id).then(response=>{
          let taskId = response.data["data"]
          let tmpStopContainerInterval = window.setInterval(() => {
            setTimeout(()=>{
              getTask(taskId).then(response=>{
                let responseStatus = response.data["status"]
                let responseData = response.data
                if (responseStatus === 1001){
                  // 一直轮训
                }else{
                  clearInterval(tmpStopContainerInterval)
                  if (responseStatus === 200){
                    this.$message({
                      message: responseData["msg"],
                      type: "success",
                    })
                    raw.status.status = "stop"
                    raw.status.start_date = ""
                    raw.status.stop_flag = false
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
      deleteContainer(container_id,raw){
        /**
         * 删除容器
         */
        this.$set(raw.status, "delete_flag", true)
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
                    this.listData(1)
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
        ImgList(this.search,false,page).then(response => {
          this.listdata = response.data.results
          this.page.total = response.data.count
        })
      }
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
  padding: 5;
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

/*p {*/
/*  height: 20px;*/
/*  line-height: 20px;*/
/*}*/
</style>
