%rebase layout globals(), css=['tags/css/tags-overview.css'], js=['tags/js/tags-overview.js'], title='Hosts tags overview', refresh=True

<div class="row">
  <span class="btn-group pull-right">
    <a href="#" id="listview" class="btn btn-small switcher quickinfo pull-right" data-original-title='List'> <i class="fa fa-align-justify"></i> </a>
    <a href="#" id="gridview" class="btn btn-small switcher active quickinfo pull-right" data-original-title='Grid'> <i class="fa fa-th"></i> </a>
  </span>
</div>

<div class="row">
	<ul id="groups" class="grid row">
		%for tag in htags:
			%nHosts=0
			%hUp=0
			%hDown=0
			%hUnreachable=0
			%hPending=0
			%business_impact = 0
			%hosts = app.datamgr.get_hosts_tagged_with(tag[0])
			%for h in hosts:
				%business_impact = max(business_impact, h.business_impact)
				%nHosts=nHosts+1
				%if h.state == 'UP':
					%hUp=hUp+1
				%elif h.state == 'DOWN':
					%hDown=hDown+1
				%elif h.state == 'UNREACHABLE':
					%hUnreachable=hUnreachable+1
				%else:
					%hPending=hPending+1
				%end
			%end
			<li class="clearfix">
				<section class="left">
					<h3>{{tag[0]}}
						%for i in range(0, business_impact-2):
						<img alt="icon state" src="/static/images/star.png">
						%end
					</h3>
          <span class="meta">
            <span class="fa-stack font-up"> <i class="fa fa-circle fa-stack-2x"></i> <i class="fa fa-check fa-stack-1x fa-inverse"></i></span> 
            <span class="num">
              %if hUp > 0:
              {{hUp}}
              %else:
              <em>{{hUp}}</em>
              %end
            </span>
            <span class="fa-stack font-unreachable"> <i class="fa fa-circle fa-stack-2x"></i> <i class="fa fa-exclamation fa-stack-1x fa-inverse"></i></span> 
            <span class="num">
              %if hUnreachable > 0:
              {{hUnreachable}}
              %else:
              <em>{{hUnreachable}}</em>
              %end
            </span>
            <span class="fa-stack font-down"> <i class="fa fa-circle fa-stack-2x"></i> <i class="fa fa-arrow-down fa-stack-1x fa-inverse"></i></span> 
            <span class="num">
              %if hDown > 0:
              {{hDown}}
              %else:
              <em>{{hDown}}</em>
              %end
            </span> 
            <span class="fa-stack font-unknown"> <i class="fa fa-circle fa-stack-2x"></i> <i class="fa fa-question fa-stack-1x fa-inverse"></i></span> 
            <span class="num">
              %if hPending > 0:
              {{hPending}}
              %else:
              <em>{{hPending}}</em>
              %end
            </span>
          </span>
				</section>
				
				<section class="right">
					%if nHosts == 1:
					<span class="sum">{{nHosts}} element</span>
					%else:
					<span class="sum">{{nHosts}} elements</span>
					%end
					<span class="darkview">
					<a href="/hosts-tag/{{tag[0]}}" class="firstbtn"><i class="fa fa-angle-double-down"></i> Details</a>
					</span>
				</section>
			</li>
		%end
	</ul>
</div>