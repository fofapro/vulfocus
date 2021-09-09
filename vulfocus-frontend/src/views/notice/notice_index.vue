<template>
  <div class="app-container">
    <div class="filter-container">
      <el-input v-model="search" style="width: 230px" size="medium"></el-input>
      <el-button class="filter-item" size="medium" style="margin-left: 10px;margin-bottom: 10px" type="primary" icon="el-icon-search" @click="handleQuery(1)">查询</el-button>
      <el-button type="primary" size="medium" icon="el-icon-edit" @click="editorButton">添加</el-button>
    </div>
    <el-table :data="tableData" border stripe align = "center" style="width: 100%" v-loading="tabLoading">
      <el-table-column type="index" width="50"> </el-table-column>
      <el-table-column prop="title" label="公告名称" :show-overflow-tooltip=true ></el-table-column>
      <el-table-column prop="update_date" :show-overflow-tooltip=true label="修改时间"> </el-table-column>
      <el-table-column :show-overflow-tooltip=true width="150" label="是否为最新发布">
        <template slot-scope="{row}">
          <el-tag v-if="row.is_newest===true">YES</el-tag>
          <el-tag v-else-if="row.is_newest===false">NO</el-tag>
        </template>
      </el-table-column>
      <el-table-column fixed="right" label="操作" width="400">
        <template slot-scope="{row}">
          <el-button style="display: inline-block;float: left;margin-left: 5px;"
                     size="mini"
                     icon="el-icon-edit"
                     type="primary"
                     v-if="row.is_public === false"
                     @click="openEdit(row)">修改</el-button>
          <el-button style="display: inline-block;float: left;margin-left: 5px;"
                     size="mini"
                     icon="el-icon-edit"
                     type="primary"
                     @click="onlyEdit(row)">查看</el-button>
          <el-button style="display: inline-block;float: left;margin-left: 5px;"
                     size="mini"
                     v-if="row.is_public === false"
                     type="primary"
                     icon="el-icon-share"
                     @click="shareWrite(row.notice_id)">发布</el-button>
          <el-button style="display: inline-block;float: left;margin-left: 5px;"
            size="mini" type="danger"
            icon="el-icon-delete"
            @click="handleDelete(row.notice_id)">删除</el-button>
          <el-tag style="display: inline-block;float: left;line-height: 28px;height: 28px; margin-left: 5px;"
                  type="success" effect="dark" v-if="row.is_public === true">
            <div style="display: inline-block;float: left"><span>已发布</span></div>
          </el-tag>
        </template>
      </el-table-column>
    </el-table>
    <div>
      <el-drawer v-if="drawerFlag" size="50%" :direction="derection" modal="false" append-to-body="true" :before-close="closeDrawer" :visible="drawer">
        <el-input style="width: 600px;margin-bottom: 20px" v-model="title" >
          <template slot="prepend" style="color: black">公告标题</template>
        </el-input>
        <div style="margin-right: 10px">
          <el-button v-if="drawerFlag===true" icon="el-icon-back" size="small" style="position:absolute;z-index: 9999;right:140px;top: 21px;" @click="closeEditorButton">返回</el-button>
          <el-button v-if="drawerFlag===true" icon="el-icon-edit-outline" size="small" style="position:absolute;z-index: 9999;right:60px;top: 21px;" @click="createnotice()">提交</el-button>
          <div v-if="drawerFlag" class="container">
            <markdown-editor ref="markdownEditor" v-model="notice_data" :options="{hideModeSwitch:true, previewStyle:'vertical'}"  height="400px" />
          </div>
        </div>
      </el-drawer>
    </div>
    <div>
      <el-drawer v-if="second_draw" size="60%" :direction="derection" modal="false" append-to-body="true" :before-close="closeDrawer_sec" :visible="second_draw">
        <el-main v-loading="loading">
          <el-button type="primary" icon="el-icon-edit-outline" @click="saveHandleMark(editNoticeInfo.title,editNoticeInfo.notice_id,editNoticeInfo.notice_content)" size="small" style="position:absolute;z-index: 9999;right:80px;top: 20px" v-if="loading != true">保存</el-button>
          <el-input style="width: 600px;margin-bottom: 20px" v-model="editNoticeInfo.title" >
            <template slot="prepend" style="color: black">公告标题</template>
          </el-input>
          <markdown-editor ref="markdownEditor" v-model="editNoticeInfo.notice_content" :options="{hideModeSwitch:true, previewStyle:'vertical'}"  height="500px" v-if="loading != true"/>
        </el-main>
      </el-drawer>
    </div>
    <div>
      <el-drawer v-if="view_show" size="60%" :direction="derection" modal="false" append-to-body="true" :before-close="closeViewDraw" :visible="view_show" >
        <el-main v-loading="loading">
          <el-input style="width: 600px;margin-left: 200px;margin-bottom: 20px" v-model="editNoticeInfo.title" disabled="disabled">
            <template slot="prepend" style="color: black">公告标题</template>
          </el-input>
          <ViewerEditor v-model="editNoticeInfo.notice_content" ref="viewerEditor"  :options="{hideModeSwitch:true, previewStyle:'vertical'}"  height="500px" v-if="loading != true"></ViewerEditor>
        </el-main>
      </el-drawer>
    </div>
    <div style="margin-top: 20px">
      <el-pagination :page-size="page.size" @current-change="handleQuery" layout="total, prev, pager, next, jumper"
        :total="page.total">
      </el-pagination>
    </div>
  </div>
</template>

<script>
import MarkdownEditor from '@/components/MarkdownEditor'
import ViewerEditor from '@/components/ViewerEditor'
import {create_notice,get_notice,delete_notice,public_notice,get_content} from '@/api/notice'
export default {
  name: "notice_index",
  components:{
    MarkdownEditor,
    ViewerEditor,
  },
  created(){
    this.InitTable()
  },
  data(){
    return {
      tableData:[],
      drawerFlag: false,
      view_show:false,
      drawer: true,
      second_draw:false,
      title: '',
      search:"",
      notice_data: '',
      tabLoading: '',
      derection:"btt",
      taskCheckInterval :null,
      page:{
          total: 0,
          size: 20,
        },
      editNoticeInfo:{
        title : '',
        notice_id: "",
        notice_content: '',
        is_newest: '',
        is_public: '',
      },
      loading:true,
    }
  },
  methods:{
    handleQuery(val){
      get_notice(this.search,val).then(response=>{
        this.tableData = response.data.results;
        this.page.total = response.data.count;
      })
    },
    editorButton(){
      this.drawerFlag=true;
      this.drawer = true;
    },
    closeEditorButton(){
      this.drawerFlag=false
    },
    closeDrawer(){
      this.drawer=false;
      this.loading=true;
    },
    createnotice(){
      let data = {};
      data.title = this.title;
      data.notice_content = this.notice_data;
      this.$confirm('是否确认提交?', '提示',{
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(()=>{
        create_notice(data).then(response=>{
          let data = response.data;
          if(data.code==200){
            this.$message({
                title: '成功',
                message: '提交成功!',
                type: 'success'
              });
            this.drawer = false;
            this.InitTable();
          }
          else{
            this.$message({
                title: '提交失败',
                message: data.message,
                type: 'error'
              });
          }
        }).catch(()=>{});
      })
    },
    InitTable(){
      clearInterval(this.taskCheckInterval);
      get_notice(undefined,1).then(response => {
        this.tableData = response.data.results
        this.tabLoading = false
        this.page.total = response.data.count
      })
    },
    openEdit(row){
        this.editNoticeInfo = row;
        this.second_draw = true;
        get_content(row.notice_id).then(response => {
          this.editNoticeInfo.notice_content = response.data.content;
          this.loading=false;
        })
      },
    closeDrawer_sec(){
      this.second_draw=false;
      this.loading=true;
    },
    saveHandleMark(title,notice_id, notice_content){
      let data = {};
      data.notice_id = notice_id;
      data.notice_content =notice_content;
      data.update_notice = true;
      data.title = title;
      this.$confirm('是否确认提交?', '提示',{
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(()=>{
        create_notice(data).then(response=>{
          let data = response.data;
          if(data.code==200){
            this.$message({
                title: '成功',
                message: '提交成功!',
                type: 'success'
              });
            this.second_draw = false;
          }
          else{
            this.$message({
                title: '提交失败',
                message: data.message,
                type: 'error'
              });
          }
        }).catch(()=>{});
      })
    },
    onlyEdit(row){
      this.editNoticeInfo = row;
      this.view_show=true;
      get_content(row.notice_id).then(response => {
          this.editNoticeInfo.notice_content = response.data.content;
          this.loading=false;
      })
    },
    closeViewDraw(){
      this.view_show=false;
      this.loading=true;
    },
    handleDelete(id){
      this.$confirm('确认删除?', '提示',{
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(()=>{
        delete_notice(id).then(response=>{
          let data = response.data;
          if(data.code==200){
            this.$message({
                title: '成功',
                message: '删除成功!',
                type: 'success'
              });
            this.InitTable()
          }else{
            this.$message({
                title: '失败',
                message: data.message,
                type: 'error'
              });
          }
        })
      })
    },
    shareWrite(id){
      public_notice(id).then(response=>{
        let rsp = response.data;
        if(rsp.code==200){
          this.$message({
                title: '成功',
                message: '发布成功!',
                type: 'success'
              });
          this.InitTable();
        }else{
           this.$message({
              message:rsp.message,
              type: "error",
            });
        }
      })
    }
  }
}
</script>

<style scoped>

</style>
