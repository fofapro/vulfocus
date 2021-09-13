<template>
  <div class="container" style="overflow: hidden">
    <div v-if="show === true">
      <el-table :data="notice_list" border stripe align = "center" style="width: 70%;margin: 20px auto" v-loading="tabLoading">
        <el-table-column type="index" width="50">
          <template slot-scope="scope">
            <svg-icon icon-class="email"  style="width: 30px;height: 30px" @click="read_detail(scope.row.notice_id)"/>
          </template>
        </el-table-column>
        <el-table-column label="公告" :show-overflow-tooltip=true align="center">
          <template slot-scope="scope">
            <div style="cursor: pointer;" @click="read_detail(scope.row.notice_id)">
              <div style="float: left;color: black;font-size: 20px;margin:0 auto;width:100%;height:40px;" v-if="scope.row.notification.unread==true"><p>{{scope.row.title}}</p></div>
              <div style="float: left;color: grey;font-size: 16px;margin:0 auto;width:100%;height:40px;" v-if="scope.row.notification.unread==false"><p>{{scope.row.title}}</p></div>
            </div>
          </template>
        </el-table-column>
        <el-table-column :show-overflow-tooltip=true label="发布时间" width="200" align="center">
          <template slot-scope="scope">
            <div style="float: left;color: black;font-size: 16px;margin:0 auto;width:100%;height:40px;" v-if="scope.row.notification.unread==true"><p>{{scope.row.update_date}}</p></div>
            <div style="float: left;color: grey;font-size: 16px;margin:0 auto;width:100%;height:40px;" v-if="scope.row.notification.unread==false"><p>{{scope.row.update_date}}</p></div>
          </template>
        </el-table-column>
      </el-table>
      <div style="margin-top: 20px;margin-left: 280px">
        <el-pagination :page-size="page.size" @current-change="handleQuery" layout="total, prev, pager, next, jumper"
          :total="page.total">
        </el-pagination>
      </div>
    </div>
    <div v-if="show === false" >
      <div v-loading="loading">
        <i class="el-icon-arrow-left" style="width:100px;height:20px;margin-left:40px;margin-top:20px;cursor:pointer;color:rgb(64, 158, 255)" @click="back_to_list">返回列表页</i>
        <ViewerEditor v-model="content" ref="viewerEditor"  :options="{hideModeSwitch:true, previewStyle:'vertical'}" style="width:80%;margin:20px auto;overflow:hidden;" v-if="loading != true"></ViewerEditor>
      </div>
    </div>
  </div>
</template>

<script>
import {get_public_notice,notice_detail} from '@/api/notice'
import MarkdownEditor from '@/components/MarkdownEditor'
import ViewerEditor from '@/components/ViewerEditor'
export default {
  name: "notices",
  data() {
    return {
      notice_list:[],
      activeNames:'1',
      radioTreaty:'1',
      page:{
          total: 0,
          size: 20,
        },
      taskCheckInterval:null,
      tabLoading:false,
      content:'',
      show:true,
      loading:true,
    }
  },
  components:{
    MarkdownEditor,
    ViewerEditor,
  },
  created(){
    this.InitTable()
  },
  methods: {
    InitTable(){
      clearInterval(this.taskCheckInterval);
      get_public_notice(1).then(response => {
        this.notice_list = response.data.data.results;
        this.tabLoading = false;
        this.page.total = response.data.data.count;
      })
    },
    handleQuery(val){
      get_public_notice(val).then(response=>{
        this.notice_list = response.data.data.results;
        this.page.total = response.data.data.count;
      })
    },
    read_detail(notice_id){
      this.show = false
      notice_detail(notice_id).then(response =>{
        let data = response.data;
        if(data.code==400){
        this.$message({
          title:"失败",
          message: data.msg,
          type:'error'
        })
      }else{
          this.content = data.data;
          this.loading = false;
        }
      })
    },
    back_to_list(){
      this.show=true;
      this.loading = true;
      location.reload();
    }
  }
}
</script>

<style scoped>

</style>
