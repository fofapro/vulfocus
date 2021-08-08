<!--
 * @Author: caojing
 * @Date: 2018-11-21 09:31:49
 * @LastEditors: caojing
 * @LastEditTime: 2018-11-23 14:43:14
 -->
<template>
  <div id="topoAttrWrap" :class="{active:isTopoAttrShow}">
    <h3 id="topoAttrHeader">属性设置框</h3>
    <div class="noAttrTip" v-if="JSON.stringify(nodeData) ==='{}'">
      未选择任何节点属性
    </div>
    <div v-show="isContainer">
      <el-form ref="containerForm" :model="image" label-width="80px">
        <el-form-item label="漏洞名称">
          <el-autocomplete v-model="searchImageName" style="width: 100%" size="small" placeholder="镜像名称"
                           :fetch-suggestions="querySearchImageAsync" @select="handleImageSelect"></el-autocomplete>
        </el-form-item>
        <el-form-item label="漏洞镜像">
          <el-input size="small" v-model="image.name" disabled></el-input>
        </el-form-item>
        <el-form-item label="漏洞描述">
          <el-input type="textarea" v-model="image.desc" size="small" disabled></el-input>
        </el-form-item>
        <el-form-item label="是否开放">
          <el-switch v-model="image.open"></el-switch>
        </el-form-item>
        <el-form-item label="镜像端口">
          <label>{{image.port}}</label>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" size="small" @click="handleImageOk">确定</el-button>
          <el-button size="small" @click="handleImageCancel">取消</el-button>
        </el-form-item>
      </el-form>
    </div>
    <div v-show="isNetwork">
      <el-form ref="networkForm" :model="network" label-width="80px">
        <el-form-item label="网卡名称">
          <el-autocomplete v-model="searchNetworkName" size="small" placeholder="网卡名称"
                           :fetch-suggestions="querySearchNetworkAsync" @select="handleNetworkSelect"></el-autocomplete>
        </el-form-item>
        <el-form-item label="子网">
          <el-input size="small" v-model="network.subnet" disabled></el-input>
        </el-form-item>
        <el-form-item label="网关">
          <el-input size="small" v-model="network.gateway" disabled></el-input>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" size="small" @click="handleNetworkOk">确定</el-button>
          <el-button size="small" @click="handleNetworkCancel">取消</el-button>
        </el-form-item>
      </el-form>
    </div>
    <i  class="topoAttrArrow"
        :class="{'pushIcon':!isTopoAttrShow,'pullIcon':isTopoAttrShow}"
        @click="isTopoAttrShow =!isTopoAttrShow">
      <img src="@/assets/topo/push.svg" v-if="!isTopoAttrShow">
      <img src="@/assets/topo/pull.svg" v-else>
    </i>
  </div>
</template>

<script>
import { ImgList } from '@/api/docker'
import {NetWorkList} from '@/api/network'

export default {
  name:'vTopoAttrPanel',
  props:{
      vSelectNodeData:{
          type:Object,
          default: function () {
                return {}
          }
      }
  },
  data(){
   return {
     isTopoAttrShow:false,
     isContainer : false,
     isNetwork: false,
     imageList: [],
     networkList: [],
     searchImageName: "",
     searchNetworkName: "",
     image: {
       id: '',
       vul_name: '',
       name: '',
       desc: '',
       port: '',
       open: false,
       raw: {}
     },
     network: {
       id: '',
       name: '',
       // 子网
       subnet: '',
       // 网关
       gateway: '',
       raw:{}
     }
   }
  },
  computed:{
      nodeData(){
        this.isTopoAttrShow = false
        this.imageList = false
        this.isContainer = false
        this.isNetwork = false
        let nodeData = JSON.parse(JSON.stringify(this.vSelectNodeData))
        let nodeType = nodeData["type"]
        if('Container' === nodeType){
          this.isContainer = true
          this.searchImageName = ""
          this.image = {
            id: '',
            vul_name: '',
            name: '',
            desc: '',
            port: '',
            open: false,
            raw: {}
          }
          if (JSON.stringify(nodeData.attrs) !== '{}'){
            this.searchImageName = nodeData.attrs.name
            this.image = nodeData.attrs
          }
        }else if('Network' === nodeType){
          this.isNetwork = true;
          this.searchNetworkName = ""
          this.network = {
            id: '',
            name: '',
            // 子网
            subnet: '',
            // 网关
            gateway: '',
            raw:{}
          }
          if (JSON.stringify(nodeData.attrs) !== '{}'){
            this.searchNetworkName = nodeData.attrs.name
            this.network = nodeData.attrs
          }
        }
        return nodeData
      }
  },
  components: {

  },
  methods:{
    querySearchImageAsync(queryString, cb) {
      this.imageList = []
      if (queryString == null){
        queryString = ""
      }
      ImgList(queryString).then(response => {
        let results = response.data.results
        if(results !== null){
          results.forEach((item, index, arr) => {
            if (item.is_docker_compose === false){
              this.imageList.push({"value": item["image_name"], "data": item})
            }
          });
        }
        if(this.imageList.length > 0){
          cb(this.imageList);
        }
      })
    },
    handleImageSelect(item){
      let imageData = item.data
      this.searchImageName = item.value
      this.image.id = imageData.image_id
      this.image.vul_name = imageData.image_vul_name
      this.image.name = imageData.image_name
      this.image.desc = imageData.image_desc
      this.image.port = imageData.image_port
      this.image.raw = imageData
    },
    querySearchNetworkAsync(queryString, cb){
      this.networkList = []
      if (queryString == null){
        queryString = ""
      }
      NetWorkList(queryString, 1).then(response => {
        let results = response.data.results
        if(results !== null){
          results.forEach((item, index, arr) => {
            this.networkList.push({"value": item["net_work_name"], "data":item})
          });
        }
        if(this.networkList.length > 0){
          cb(this.networkList);
        }
      })
    },
    handleNetworkSelect(item){
      let networkData = item.data
      this.searchNetworkName = item.value
      this.network.id = networkData.net_work_id
      this.network.name = networkData.net_work_name
      this.network.gateway = networkData.net_work_gateway
      this.network.subnet = networkData.net_work_subnet
      this.network.raw = networkData
    },
    handleImageOk(){
      if(this.image.id === ''){
        this.$message({
          type: "error",
          message: "请选择镜像"
        });
      }else{
        // attrs
        this.vSelectNodeData.attrs = this.image
        this.$message({
          type: "success",
          message: "设置成功"
        });
        this.isTopoAttrShow = false
        this.imageList = []
        this.isContainer = false
        this.isNetwork = false
        this.searchImageName = ""
        this.image = {
          id: '',
          name: '',
          desc: '',
          port: '',
          open: false
        }
      }
    },
    handleImageCancel(){
      this.isTopoAttrShow = false
    },
    handleNetworkOk(){
      if(this.network.id === ''){
        this.$message({
          type: "error",
          message: "请选择网卡"
        });
      }else{
        this.vSelectNodeData.attrs = this.network
        this.$message({
          type: "success",
          message: "设置成功"
        });
        this.isTopoAttrShow = false
        this.isContainer = false
        this.isNetwork = false
        this.networkList = []
        this.searchImageName = ""
        this.network ={
          id: '',
          name: '',
          // 子网
          subnet: '',
          // 网关
          gateway: '',
          raw:{}
        }
      }
    },
    handleNetworkCancel(){
      this.isTopoAttrShow = false
    }
  }
}
</script>

<style lang="less">

</style>
<style lang="less" scoped>
#topoAttrWrap{display:flex;flex-direction:column;height:100%;width:400px;position:absolute;top:0;right:-400px;background:#fff;border-left:1px solid darken(#f3f3f3,10%);transition:all 1s;box-sizing:border-box;
    &.active{right:0;box-shadow:-1px 0px 15px  #f3f3f3}
    .topoAttrArrow{color:#f3f3f3;font-size:20px;position:absolute;top:50%;translate:transform(0 -50%);z-index:200;cursor:pointer;
        &.pushIcon{left:-17px;}
        &.pullIcon{left:-2px;}
    }
    #topoAttrHeader{padding:10px 0;background-color:darken(#f3f3f3,5%);color:#525252;text-align:center;font-weight:400;font-size:14px;}
    .noAttrTip{padding:50px;text-align:center;flex:1;}
    .topoAttrBody{flex:1;display:flex;flex-direction:column;
        .topoAttrMain{overflow-y: scroll;flex:1;padding:20px 15px;box-sizing:border-box;}
        .topoAttrFooter{padding:30px 0;display:flex;justify-content: center;align-items:center;}
    }
}
</style>
