<template>
  <div class="app-container">
    <el-dialog :visible.sync="centerDialogVisible" title="添加" width="65%">
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
              <el-form-item label="标签" >
                <div class="tag-group">
                  <el-row>
                    <el-col :span="2.5">
                      <el-button type='primary' size="mini" style="width: 80px" class="tag-group__title">漏洞类型</el-button>
                    </el-col>
                    <el-tag style="margin-left: 10px" :key="index" v-for="(tag, index) in vulInfo.HoleType" closable :disable-transitions="false" @close="handleClose(tag, 'HoleType', 'newtag')">
                      {{tag}}
                    </el-tag>
                    <el-autocomplete
                      v-if="inputVisible1"
                      ref="saveTagInput1"
                      @keyup.enter.native="handleInputConfirm1('newtag')"
                      popper-class="my-autocomplete"
                      v-model="inputValue1"
                      :fetch-suggestions="((queryString,cb)=>{querySearch(queryString,cb,type='inputValue1')})"
                      placeholder="请输入内容"
                      @select="handleSel">
                      <template slot-scope="{ item }">
                        <div class="name">{{ item.value }}</div>
                      </template>
                    </el-autocomplete>
                    <el-button v-else class="button-new-tag" size="small" @click="showInput1">+ New Tag</el-button>
                  </el-row>
                </div>
                <div class="tag-group">
                  <el-row>
                    <el-col :span="2.5">
                      <el-button  type='primary' size="mini" style="width: 80px" class="tag-group__title">开发语言</el-button>
                    </el-col>
                    <el-tag style="margin-left: 10px" :key="index" v-for="(tag, index) in vulInfo.devLanguage" closable :disable-transitions="false" @close="handleClose(tag,'devLanguage', 'newtag')">
                    {{tag}}
                    </el-tag>
                    <el-autocomplete
                      v-if="inputVisible2"
                      ref="saveTagInput2"
                      @keyup.enter.native="handleInputConfirm2('newtag')"
                      popper-class="my-autocomplete"
                      v-model="inputValue2"
                      :fetch-suggestions="((queryString,cb)=>{querySearch(queryString,cb,type='inputValue2')})"
                      placeholder="请输入内容"
                      @select="handleSel">
                      <template slot-scope="{ item }">
                        <div class="name">{{ item.value }}</div>
                      </template>
                    </el-autocomplete>
                    <el-button v-else class="button-new-tag" size="small" @click="showInput2">+ New Tag</el-button>
                  </el-row>
                </div>
                <div class="tag-group">
                  <el-row>
                    <el-col :span="2.5">
                      <el-button type='primary' size="mini" style="width: 80px" class="tag-group__title">数据库</el-button>
                    </el-col>
                    <el-tag style="margin-left: 10px" :key="index" v-for="(tag, index) in vulInfo.devDatabase" closable :disable-transitions="false" @close="handleClose(tag, 'devDatabase', 'newtag')">
                    {{tag}}
                    </el-tag>
                    <el-autocomplete
                      v-if="inputVisible3"
                      ref="saveTagInput3"
                      @keyup.enter.native="handleInputConfirm3('newtag')"
                      popper-class="my-autocomplete"
                      v-model="inputValue3"
                      :fetch-suggestions="((queryString,cb)=>{querySearch(queryString,cb,type='inputValue3')})"
                      placeholder="请输入内容"
                      @select="handleSel">
                      <template slot-scope="{ item }">
                        <div class="name">{{ item.value }}</div>
                      </template>
                    </el-autocomplete>
                    <el-button v-else class="button-new-tag" size="small" @click="showInput3">+ New Tag</el-button>
                  </el-row>
                </div>
                <div class="tag-group">
                  <el-row>
                    <el-col :span="2.5">
                      <el-button type='primary' size="mini" style="width: 80px" class="tag-group__title">分类</el-button>
                    </el-col>
                    <el-tag style="margin-left: 10px" :key="index" v-for="(tag, index) in vulInfo.devClassify" closable :disable-transitions="false" @close="handleClose(tag, 'devClassify', 'newtag')">
                    {{tag}}
                    </el-tag>
                    <el-autocomplete
                      v-if="inputVisible4"
                      ref="saveTagInput4"
                      @keyup.enter.native="handleInputConfirm4('newtag')"
                      popper-class="my-autocomplete"
                      v-model="inputValue4"
                      :fetch-suggestions="((queryString,cb)=>{querySearch(queryString,cb,type='inputValue4')})"
                      placeholder="请输入内容"
                      @select="handleSel">
                      <template slot-scope="{ item }">
                        <div class="name">{{ item.value }}</div>
                      </template>
                    </el-autocomplete>
                    <el-button v-else class="button-new-tag" size="small" @click="showInput4">+ New Tag</el-button>
                  </el-row>
                </div>
              </el-form-item>
              <el-form-item label="Rank">
                <el-input-number v-model="vulInfo.rank" :min="0.5" :max="5.0" :precision="1" :step="0.5" size="medium"></el-input-number>
                <el-tooltip content="默认分数为2.5分，可根据漏洞的利用难度进行评判" placement="top">
                  <i class="el-icon-question"></i>
                </el-tooltip>
              </el-form-item>
              <el-form-item label="描述">
                <el-input type="textarea" v-model="vulInfo.desc" size="medium"></el-input>
              </el-form-item>
              <el-form-item label="flag">
                <el-switch v-model="vulInfo.is_flag"></el-switch>
                <el-tooltip content="是否开启flag" placement="top">
                  <i class="el-icon-question"></i>
                </el-tooltip>
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
          <el-tab-pane name="addcompose" label="Compose编译">
            <compose />
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
    <el-dialog :visible.sync="editShow" @close="closeDialog">
      <el-tabs  v-model="activeName">
        <el-tab-pane label="修改" name="first">
          <el-form label-width="80px" v-loading="editLoding" element-loading-text="修改中">
          <el-form-item label="漏洞名称">
            <el-input v-model="editVulInfo.image_vul_name" size="medium"></el-input>
          </el-form-item>
          <el-form-item label="镜像">
            <el-input v-model="editVulInfo.image_name" disabled></el-input>
          </el-form-item>
          <el-form-item label="标签" >
            <div class="tag-group">
              <el-row>
                <el-col :span="2.5">
                  <el-button type='primary' size="mini" style="width: 80px" class="tag-group__title">漏洞类型</el-button>
                </el-col>
                <el-tag style="margin-left: 10px" :key="index" v-for="(tag, index) in editVulInfo.HoleType" closable :disable-transitions="false" @close="handleClose(tag, 'HoleType')">
                  {{tag}}
                </el-tag>
                <el-autocomplete
                  v-if="inputVisible1"
                  ref="saveTagInput1"
                  @keyup.enter.native="handleInputConfirm1"
                  popper-class="my-autocomplete"
                  v-model="inputValue1"
                  :fetch-suggestions="((queryString,cb)=>{querySearch(queryString,cb,type='inputValue1')})"
                  placeholder="请输入内容"
                  @select="handleSel">
                  <template slot-scope="{ item }">
                    <div class="name">{{ item.value }}</div>
                  </template>
                </el-autocomplete>
                <el-button v-else class="button-new-tag" size="small" @click="showInput1">+ New Tag</el-button>
              </el-row>
            </div>
            <div class="tag-group">
              <el-row>
                <el-col :span="2.5">
                  <el-button  type='primary' size="mini" style="width: 80px" class="tag-group__title">开发语言</el-button>
                </el-col>
                <el-tag style="margin-left: 10px" :key="index" v-for="(tag, index) in editVulInfo.devLanguage" closable :disable-transitions="false" @close="handleClose(tag,'devLanguage')">
                {{tag}}
                </el-tag>
                <el-autocomplete
                  v-if="inputVisible2"
                  ref="saveTagInput2"
                  @keyup.enter.native="handleInputConfirm2"
                  popper-class="my-autocomplete"
                  v-model="inputValue2"
                  :fetch-suggestions="((queryString,cb)=>{querySearch(queryString,cb,type='inputValue2')})"
                  placeholder="请输入内容"
                  @select="handleSel">
                  <template slot-scope="{ item }">
                    <div class="name">{{ item.value }}</div>
                  </template>
                </el-autocomplete>
                <el-button v-else class="button-new-tag" size="small" @click="showInput2">+ New Tag</el-button>
              </el-row>
            </div>
            <div class="tag-group">
              <el-row>
                <el-col :span="2.5">
                  <el-button type='primary' size="mini" style="width: 80px" class="tag-group__title">数据库</el-button>
                </el-col>
                <el-tag style="margin-left: 10px" :key="index" v-for="(tag, index) in editVulInfo.devDatabase" closable :disable-transitions="false" @close="handleClose(tag, 'devDatabase')">
                {{tag}}
                </el-tag>
                <el-autocomplete
                  v-if="inputVisible3"
                  ref="saveTagInput3"
                  @keyup.enter.native="handleInputConfirm3"
                  popper-class="my-autocomplete"
                  v-model="inputValue3"
                  :fetch-suggestions="((queryString,cb)=>{querySearch(queryString,cb,type='inputValue3')})"
                  placeholder="请输入内容"
                  @select="handleSel">
                  <template slot-scope="{ item }">
                    <div class="name">{{ item.value }}</div>
                  </template>
                </el-autocomplete>
                <el-button v-else class="button-new-tag" size="small" @click="showInput3">+ New Tag</el-button>
              </el-row>
            </div>
            <div class="tag-group">
              <el-row>
                <el-col :span="2.5">
                  <el-button type='primary' size="mini" style="width: 80px" class="tag-group__title">开发框架</el-button>
                </el-col>
                <el-tag style="margin-left: 10px" :key="index" v-for="(tag, index) in editVulInfo.devClassify" closable :disable-transitions="false" @close="handleClose(tag, 'devClassify')">
                {{tag}}
                </el-tag>
                <el-autocomplete
                  v-if="inputVisible4"
                  ref="saveTagInput4"
                  @keyup.enter.native="handleInputConfirm4"
                  popper-class="my-autocomplete"
                  v-model="inputValue4"
                  :fetch-suggestions="((queryString,cb)=>{querySearch(queryString,cb,type='inputValue4')})"
                  placeholder="请输入内容"
                  @select="handleSel">
                  <template slot-scope="{ item }">
                    <div class="name">{{ item.value }}</div>
                  </template>
                </el-autocomplete>
                <el-button v-else class="button-new-tag" size="small" @click="showInput4">+ New Tag</el-button>
              </el-row>
            </div>
          </el-form-item>
          <el-form-item label="Rank">
            <el-input-number v-model="editVulInfo.rank" :min="0.0" :max="5.0" :precision="1" :step="0.5" size="medium"></el-input-number>
            <el-tooltip content="默认分数为2.5分，可根据漏洞的利用难度进行评判" placement="top">
              <i class="el-icon-question"></i>
            </el-tooltip>
          </el-form-item>
          <el-form-item label="Flag">
            <el-switch v-model="editVulInfo.is_flag"></el-switch>
            <el-tooltip content="是否开启flag" placement="top">
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
        </el-tab-pane>
        <el-tab-pane id="compose-update" label="Compose修改" name="secnd" v-if="editVulInfo.is_docker_compose === true">
          <span slot="label"><i class="el-icon-document"></i>DockerCompose修改</span>
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
                  <el-button @click="update_compose_build" type="primary" size="mini">编译</el-button>
                </div>
              </el-col>
              <el-col :span="22" style="margin-top: 1px">
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
    </el-dialog>
    <div class="filter-container">
      <el-input v-model="search" style="width: 230px;" size="medium"></el-input>
      <el-button class="filter-item" size="medium" style="margin-left: 10px;margin-bottom: 10px" type="primary" icon="el-icon-search" @click="SearchQuery(1)">
        查询
      </el-button>
      <el-button class="filter-item" size="medium" style="margin-left: 10px;margin-bottom: 10px" type="primary" icon="el-icon-edit" @click="openCreate">
        添加
      </el-button>
      <el-button v-if="loading===false" class="filter-item" @click="getWebsiteData" size="medium" style="float: right;margin-bottom: 10px" type="primary" icon="el-icon-refresh-left">
        一键同步
      </el-button>
      <el-button v-else-if="loading===true" type="primary" :loading="true" style="float: right;margin-bottom: 10px" >同步中</el-button>
    </div>
    <el-table :data="tableData" border stripe align = "center" style="width: 100%" v-loading="tabLoading">
      <el-table-column type="index" width="50"> </el-table-column>
      <el-table-column prop="image_name" label="镜像名称" :show-overflow-tooltip=true ></el-table-column>
      <el-table-column prop="image_vul_name" label="漏洞名称" :show-overflow-tooltip=true></el-table-column>
      <el-table-column prop="image_port" label="端口" width="150"></el-table-column>
      <el-table-column prop="rank" label="分数" width="50"></el-table-column>
      <el-table-column label="标签" width="260">
        <template slot-scope="{row}" v-if="row.degree.length > 0 && row.degree !==''">
          <el-tag v-for="i in row.degree" style="margin-left: 2px;">{{i}}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="image_desc" :show-overflow-tooltip=true label="描述"> </el-table-column>
      <el-table-column prop="update_date" :show-overflow-tooltip=true label="修改时间"> </el-table-column>
      <el-table-column fixed="right" label="操作" width="280">
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
  import { ImgList,get_website_imgs } from "@/api/docker"
  import { search } from "@/api/utils"
  import { ImageAdd, ImageDelete,ImageLocal,ImageLocalAdd,ImageShare,ImageDownload,ImageEdit } from "@/api/image"
  import { containerDel } from '@/api/container'
  import { getTask,batchTask,progressTask } from '@/api/tasks'
  import MarkdownEditor from '@/components/MarkdownEditor'
  import Compose from "./components/Compose";
  import { build_compose,update_build_compose,uploadFile,deleteFile } from "@/api/layout"
  export default {
    inject: ['reload'],
    name: 'index',
    components: {
      MarkdownEditor,
      Compose
    },
    data() {
      return {
        markstatus: false,
        tableData: [],
        search: "",
        real_search:"",
        localSearch: "",
        centerDialogVisible: false,
        startCon: false,
        vulInfo: {
          rank: "",
          name: "",
          vul_name: "",
          desc: "",
          degree:[],
          is_flag: true,
          HoleType: [],
          devLanguage:[],
          devDatabase:[],
          devClassify:[],
        },
        activeName: 'first',
        HoleType: [],
        devLanguage:[],
        devDatabase:[],
        devClassify:[],
        inputVisible1: false,
        inputVisible2: false,
        inputVisible3: false,
        inputVisible4: false,
        inputValue1: '',
        inputValue2: '',
        inputValue3: '',
        inputValue4: '',
        editShow: false,
        editLoding: false,
        tabLoading: true,
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
        languageList:[
          {value:"Java", lable:"Java"},
          {value:"Python", lable:"Python"},
          {value:"C++", lable:"C++"},
          {value:"C#", lable:"C#"},
          {value:"VisualBasic", lable:"VisualBasic"},
          {value:"JavaScript", lable:"JavaScript"},
          {value:"HTML", lable:"HTML"},
          {value:"PHP", lable:"PHP"},
          {value:"R", lable:"R"},
          {value:"Swift", lable:"Swift"},
          {value:"Go", lable:"Go"},
          {value:"Ruby", lable:"Ruby"},
          {value:"Perl", lable:"Perl"},
          {value:"Asp", lable:"Asp"},
          {value:".Net", lable:".Net"},
        ],
        databaseList:[
          {value:"Oracle", lable:"Oracle"},
          {value:"MySQL", lable:"MySQL"},
          {value:"Microsoft SQL Server", lable:"Microsoft SQL Server"},
          {value:"PostgreSQL", lable:"PostgreSQL"},
          {value:"MongoDB", lable:"MongoDB"},
          {value:"IBM Db2", lable:"IBM Db2"},
          {value:"Elasticsearch", lable:"Elasticsearch"},
          {value:"Redis", lable:"Redis"},
          {value:"SQLite", lable:"SQLite"},
          {value:"Cassandra", lable:"Cassandra"},
          {value:"Microsoft Access", lable:"Microsoft Access"},
          {value:"MariaDB Relational", lable:"MariaDB Relational"},
          {value:"Splunk", lable:"Splunk"},
          {value:"Hive", lable:"Hive"},
          {value:"Teradata", lable:"Teradata"},
        ],
        classifyList:[
          {value:"全部", lable:"全部"},
          {value:"Bootstrap", lable:"Bootstrap"},
          {value:"Angular", lable:"Angular"},
          {value:"Jquery", lable:"Jquery"},
          {value:"react", lable:"react"},
          {value:"vue", lable:"vue"},
          {value:"Zepto", lable:"Zepto"},
          {value:"CakePHP", lable:"CakePHP"},
          {value:"Django", lable:"Django"},
          {value:"Ruby on Rails", lable:"Ruby on Rails"},
          {value:"Flask", lable:"Flask"},
          {value:"Phoenix", lable:"Phoenix"},
          {value:"Spring Boot", lable:"Spring Boot"},
          {value:"Laravel", lable:"Laravel"},
        ],
        editVulInfo:{
          rank: "",
          image_name: "",
          image_id: "",
          image_vul_name: "",
          image_desc: "",
          degree:[],
          is_flag: true,
          is_docker_compose:false,
          docker_compose_yml:'',
          HoleType: [],
          devLanguage:[],
          devDatabase:[],
          devClassify:[],
        },
        compose_content:"",
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
        },
        value:[],
        newFile: new FormData(),
        fileList:[],
        restaurants: [],
        state: '',
        current_page:1,
      }
    },
    mounted() {
      this.restaurants = this.degreeList;
    },
    created() {
      this.initTableData()
      this.initSummariesList()
    },
    methods:{
      getWebsiteData(){
         this.loading=true
         get_website_imgs().then(response=>{
           let data = response.data
           if (data.code===200){
             this.$message(
             {
              message:"同步完成",
              type:"success"
             })
             this.reload()
             }else{
             this.$message({
              message:"同步失败",
              type:"error"
             })
             }
           this.loading=false
         })
       },
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
      querySearch(queryString, cb, type) {
        let types = type
        if (type){
          if (types === 'inputValue1') {
            var restaurants = this.degreeList;
          }
          if (types === 'inputValue2') {
            var restaurants = this.languageList;
          }
          if (types === 'inputValue3') {
            var restaurants = this.databaseList;
          }
          if (types === 'inputValue4') {
            var restaurants = this.classifyList;
          }
        }else {
          var restaurants = []
        }
        var results = queryString ? restaurants.filter(this.createFilter(queryString)) : restaurants;
        // 调用 callback 返回建议列表的数据
        cb(results);
      },
      createFilter(queryString) {
        return (restaurant) => {
          return (restaurant.value.toLowerCase().indexOf(queryString.toLowerCase()) === 0);
        };
      },
      handleSel(item) {
      },
      initTableData(){
        clearInterval(this.taskCheckInterval)
        ImgList(undefined, true, 1).then(response => {
          this.tableData = response.data.results
          this.tabLoading = false
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
        this.vulInfo.degree = []
        this.vulInfo.is_flag = true
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
        this.activeName = 'first'
        this.editShow = true
        this.editVulInfo = row
        this.compose_content = row.status.json_yml
      },
      handleEditImage(){
        this.editLoding = true
        let all_degree = {
          'HoleType':this.editVulInfo.HoleType,
          'devLanguage':this.editVulInfo.devLanguage,
          'devDatabase':this.editVulInfo.devDatabase,
          'devClassify':this.editVulInfo.devClassify,
        }
        this.editVulInfo.degree = all_degree
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
            ImgList(this.search, true, this.current_page).then(response => {
              this.tableData = response.data.results
              this.page.total = response.data.count
            })
          }else{
            this.$message({
              message: msg,
              type: 'error'
            });
          }
        })
      },
      closeDialog() {
          this.editShow=false
          this.editVulInfo = []
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
        let all_degree = {
          'HoleType':this.vulInfo.HoleType,
          'devLanguage':this.vulInfo.devLanguage,
          'devDatabase':this.vulInfo.devDatabase,
          'devClassify':this.vulInfo.devClassify,
        }
        // this.vulInfo.degree = all_degree
        formData.set("rank", this.vulInfo.rank)
        formData.set("image_name", this.vulInfo.name)
        formData.set("image_vul_name", this.vulInfo.vul_name)
        formData.set("image_desc", this.vulInfo.desc)
        formData.set("HoleType", this.vulInfo.HoleType)
        formData.set("devLanguage", this.vulInfo.devLanguage)
        formData.set("devDatabase", this.vulInfo.devDatabase)
        formData.set("devClassify", this.vulInfo.devClassify)
        formData.set("is_flag", this.vulInfo.is_flag)
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
                clearInterval(this.taskCheckInterval)
                ImgList(this.real_search, true, this.current_page).then(response => {
                  this.tableData = response.data.results
                  this.tabLoading = false
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
          ImgList(this.real_search, true, this.current_page).then(response => {
                this.tableData = response.data.results
                this.tabLoading = false
                this.page.total = response.data.count
                this.tableData.forEach((item, index, arr) => {
                  let image_name = item.image_name
                  if (this.tmpImageNameList.indexOf(image_name) > -1) {
                        this.$notify({
                          title: '成功',
                          message: image_name + " 添加成功",
                          type: 'success'
                        });
                      }
                })
                let tmpTableData = response.data.results
                this.taskCheckInterval = window.setInterval(() => {
                  setTimeout(() => {
                    this.checkTask(tmpTableData)
                  }, 0)
                }, 2000)
              })
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
            if(data.status === 200) {
              this.$message({
                title: '成功',
                message: '删除成功!',
                type: 'success'
              });
              clearInterval(this.taskCheckInterval);
              if(this.tableData.length === 1){
                this.current_page -= 1;
                if(this.current_page == 0){
                  this.current_page =1;
                }
              };
              ImgList(this.real_search, true, this.current_page).then(response => {
                this.tableData = response.data.results
                this.tabLoading = false
                this.page.total = response.data.count
                this.tableData.forEach((item, index, arr) => {
                  let image_name = item.image_name
                  if (this.tmpImageNameList.indexOf(image_name) > -1) {
                        this.$notify({
                          title: '成功',
                          message: image_name + " 添加成功",
                          type: 'success'
                        });
                      }
                })
                let tmpTableData = response.data.results
                this.taskCheckInterval = window.setInterval(() => {
                  setTimeout(() => {
                    this.checkTask(tmpTableData)
                  }, 0)
                }, 2000)
              })
            }
            else{
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
        this.current_page = val
        ImgList(this.real_search, true, val).then(response => {
          this.tableData = response.data.results
          this.page.total = response.data.count
        }).catch(() => {})
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
              if(status !== 1 && status !== 2){
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
                        ImgList(this.search, true, this.current_page).then(response => {
                this.tableData = response.data.results
                this.page.total = response.data.count
              })
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
      update_compose_build(){
        let data = {}
        data.compose_content = this.compose_content
        data.image_id = this.editVulInfo.image_id
        update_build_compose(data).then(response=>{
          if (response.data.code === 200){
            this.$message({
              title: '构建任务创建成功',
              message: response.data.message,
              type: 'success'
            });
            this.editShow = false
            this.initTableData()
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
      handleClose(tag, type, tags) {
        let types = type
        if (tags === 'newtag'){
          if (types === 'HoleType') {
            this.vulInfo.HoleType.splice(this.vulInfo.HoleType.indexOf(tag), 1);
          }
          if (types === 'devLanguage') {
            this.vulInfo.devLanguage.splice(this.vulInfo.devLanguage.indexOf(tag), 1);
          }
          if (types === 'devDatabase') {
            this.vulInfo.devDatabase.splice(this.vulInfo.devDatabase.indexOf(tag), 1);
          }
          if (types === 'devClassify') {
            this.vulInfo.devClassify.splice(this.vulInfo.devClassify.indexOf(tag), 1);
          }
        }else {
          if (types === 'HoleType') {
            this.editVulInfo.HoleType.splice(this.editVulInfo.HoleType.indexOf(tag), 1);
          }
          if (types === 'devLanguage') {
            this.editVulInfo.devLanguage.splice(this.editVulInfo.devLanguage.indexOf(tag), 1);
          }
          if (types === 'devDatabase') {
            this.editVulInfo.devDatabase.splice(this.editVulInfo.devDatabase.indexOf(tag), 1);
          }
          if (types === 'devClassify') {
            this.editVulInfo.devClassify.splice(this.editVulInfo.devClassify.indexOf(tag), 1);
          }
        }
      },
      showInput1() {
        this.inputVisible1 = true;
        this.$nextTick(_ => {
          this.$refs.saveTagInput1.$refs.input.focus();
        });
      },
      showInput2() {
        this.inputVisible2 = true;
        this.$nextTick(_ => {
          this.$refs.saveTagInput2.$refs.input.focus();
        });
      },
      showInput3() {
        this.inputVisible3 = true;
        this.$nextTick(_ => {
          this.$refs.saveTagInput3.$refs.input.focus();
        });
      },
      showInput4() {
        this.inputVisible4 = true;
        this.$nextTick(_ => {
          this.$refs.saveTagInput4.$refs.input.focus();
        });
      },
      handleInputConfirm1(tag) {
        let inputValue = this.inputValue1;
        if (tag === 'newtag'){
          if (this.vulInfo.HoleType === null){
            this.vulInfo.HoleType = [];
          }
          this.vulInfo.HoleType.push(inputValue);
        }else {
          if (this.editVulInfo.HoleType === null){
            this.editVulInfo.HoleType = [];
          }
          this.editVulInfo.HoleType.push(inputValue);
        }
        this.inputVisible1 = false;
        this.inputValue1 = '';
      },
      handleInputConfirm2(tag) {
        let inputValue = this.inputValue2;
        if (tag === 'newtag'){
          if (this.vulInfo.devLanguage === null){
            this.vulInfo.devLanguage = [];
          }
          this.vulInfo.devLanguage.push(inputValue);
        }else {
          if (this.editVulInfo.devLanguage === null){
            this.editVulInfo.devLanguage = [];
          }
          this.editVulInfo.devLanguage.push(inputValue);
        }
        this.inputVisible2 = false;
        this.inputValue2 = '';
      },
      handleInputConfirm3(tag) {
        let inputValue = this.inputValue3;
        if (tag === 'newtag'){
          if (this.vulInfo.devDatabase === null){
              this.vulInfo.devDatabase = [];
          }
          this.vulInfo.devDatabase.push(inputValue);
        }else {
          if (this.editVulInfo.devDatabase === null){
              this.editVulInfo.devDatabase = [];
          }
          this.editVulInfo.devDatabase.push(inputValue);
        }
        this.inputVisible3 = false;
        this.inputValue3 = '';
      },
      handleInputConfirm4(tag) {
        let inputValue = this.inputValue4;
        if (tag === 'newtag'){
          if (this.vulInfo.devClassify === null){
              this.vulInfo.devClassify = [];
          }
          this.vulInfo.devClassify.push(inputValue);
        }else {
          if (this.editVulInfo.devClassify === null){
              this.editVulInfo.devClassify = [];
          }
          this.editVulInfo.devClassify.push(inputValue);
        }
        this.inputVisible4 = false;
        this.inputValue4 = '';
      },
      SearchQuery(page){
        this.real_search = this.search;
        this.current_page = page;
        ImgList(this.real_search, true, page).then(response => {
          this.tableData = response.data.results;
          this.page.total = response.data.count;
        })
      }
    }
  }
</script>

<style scoped>
  .el-tag + .el-tag {
    margin-left: 10px;
  }
  .button-new-tag {
    margin-left: 10px;
    height: 32px;
    line-height: 30px;
    padding-top: 0;
    padding-bottom: 0;
  }
  .input-new-tag {
    width: 90px;
    margin-left: 10px;
    vertical-align: bottom;
  }

</style>
